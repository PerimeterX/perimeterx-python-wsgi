from Crypto.Cipher import AES
from time import time
import base64
import hmac
import hashlib
import json
import sys, traceback
import binascii
import struct

_trans_5C = b"".join(chr(x ^ 0x5C) for x in range(256))
_trans_36 = b"".join(chr(x ^ 0x36) for x in range(256))


def pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None):
    """Password based key derivation function 2 (PKCS #5 v2.0)

    This Python implementations based on the hmac module about as fast
    as OpenSSL's PKCS5_PBKDF2_HMAC for short passwords and much faster
    for long passwords.
    """
    if not isinstance(hash_name, str):
        raise TypeError(hash_name)

    if not isinstance(password, (bytes, bytearray)):
        password = bytes(buffer(password))
    if not isinstance(salt, (bytes, bytearray)):
        salt = bytes(buffer(salt))

    # Fast inline HMAC implementation
    inner = hashlib.new(hash_name)
    outer = hashlib.new(hash_name)
    blocksize = getattr(inner, 'block_size', 64)
    if len(password) > blocksize:
        password = hashlib.new(hash_name, password).digest()
    password = password + b'\x00' * (blocksize - len(password))
    inner.update(password.translate(_trans_36))
    outer.update(password.translate(_trans_5C))

    def prf(msg, inner=inner, outer=outer):
        # PBKDF2_HMAC uses the password as key. We can re-use the same
        # digest objects and just update copies to skip initialization.
        icpy = inner.copy()
        ocpy = outer.copy()
        icpy.update(msg)
        ocpy.update(icpy.digest())
        return ocpy.digest()

    if iterations < 1:
        raise ValueError(iterations)
    if dklen is None:
        dklen = outer.digest_size
    if dklen < 1:
        raise ValueError(dklen)

    hex_format_string = "%%0%ix" % (hashlib.new(hash_name).digest_size * 2)

    dkey = b''
    loop = 1
    while len(dkey) < dklen:
        prev = prf(salt + struct.pack(b'>I', loop))
        rkey = int(binascii.hexlify(prev), 16)
        for i in xrange(iterations - 1):
            prev = prf(prev)
            rkey ^= int(binascii.hexlify(prev), 16)
        loop += 1
        dkey += binascii.unhexlify(hex_format_string % rkey)

    return dkey[:dklen]


def is_cookie_expired(cookie):
    """
    Checks if cookie validity time expired.
    :param cookie: risk object
    :type cookie: dictionary
    :return: Returns True if valid and False if not
    :rtype: Bool
    """
    now = int(round(time() * 1000))
    expire = cookie[u't']
    return now > expire


def is_cookie_valid(cookie, cookie_key, ctx):
    """
    Checks if cookie hmac signing match the request.
    :param cookie: risk object
    :param cookie_key: cookie secret key
    :param ctx: perimeterx request context object
    :type cookie: dictionary
    :type cookie_key: string
    :type ctx: dictionary
    :return: Returns True if valid and False if not
    :rtype: Bool
    """
    user_agent = ctx['user_agent']
    msg = str(cookie['t']) + str(cookie['s']['a']) + str(cookie['s']['b']) + str(cookie['u']) + str(
        cookie['v']) + user_agent

    valid_digest = cookie['h']
    try:
        calculated_digest = hmac.new(cookie_key, msg, hashlib.sha256).hexdigest()
    except:
        return False

    return valid_digest == calculated_digest


def decrypt_cookie(cookie_key, cookie):
    """
    Decrypting the PerimeterX risk cookie using AES
    :param cookie_key: cookie secret key
    :param cookie: risk cookie - encrypted
    :type cookie_key: string
    :type cookie: string
    :return: Returns decrypted value if valid and False if not
    :rtype: Bool|String
    """
    try:
        parts = cookie.split(':', 3)
        if len(parts) != 3:
            return False
        salt = base64.b64decode(parts[0])
        iterations = int(parts[1])
        if iterations < 1 or iterations > 10000:
            return False
        data = base64.b64decode(parts[2])
        dk = pbkdf2_hmac('sha256', cookie_key, salt, iterations, dklen=48)
        key = dk[:32]
        iv = dk[32:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        unpad = lambda s: s[0:-ord(s[-1])]
        plaintext = unpad(cipher.decrypt(data))
        return plaintext
    except:
        print traceback.format_exception(*sys.exc_info())
        return False


def verify(ctx, config):
    """
    main verification function, verifying the content of the perimeterx risk cookie if exists
    :param ctx: perimeterx request context object
    :param config: global configurations
    :type ctx: dictionary
    :type config: dictionary
    :return: Returns True if verification succeeded and False if not
    :rtype: Bool
    """
    logger = config['logger']
    px_cookie = ctx['_px']
    try:
        if not px_cookie:
            logger.debug('No risk cookie on the request')
            ctx['s2s_call_reason'] = 'no_cookie'
            return False

        decrypted_cookie = decrypt_cookie(config['cookie_key'], px_cookie)

        if not decrypted_cookie:
            logger.error('Cookie decryption failed')
            ctx['s2s_call_reason'] = 'cookie_decryption_failed'
            return False

        decoded_cookie = json.loads(decrypted_cookie)
        try:
            decoded_cookie['s'], decoded_cookie['s']['b'], decoded_cookie['u'], decoded_cookie['t'], decoded_cookie['v']
        except:
            logger.error('Cookie decryption failed')
            ctx['s2s_call_reason'] = 'cookie_decryption_failed'
            return False

        ctx['risk_score'] = decoded_cookie['s']['b']
        ctx['uuid'] = decoded_cookie.get('u', '')
        ctx['vid'] = decoded_cookie.get('v', '')
        ctx['decoded_cookie'] = decoded_cookie

        if decoded_cookie['s']['b'] >= config['blocking_score']:
            ctx['block_reason'] = 'cookie_high_score'
            logger.debug('Cookie with high score: ' + str(ctx['risk_score']))
            return True

        if is_cookie_expired(decoded_cookie):
            ctx['s2s_call_reason'] = 'cookie_expired'
            logger.debug('Cookie expired')
            return False

        if not is_cookie_valid(decoded_cookie, config['cookie_key'], ctx):
            logger.debug('Cookie validation failed')
            ctx['s2s_call_reason'] = 'cookie_validation_failed'
            return False

        logger.debug('Cookie validation passed with good score: ' + str(ctx['risk_score']))
        return True
    except:
        logger.debug('Cookie validation failed')
        ctx['s2s_call_reason'] = 'cookie_validation_failed'
        return False
