import hashlib
from px_constants import TRANS_5C
from px_constants import TRANS_36
import struct
import binascii
import hmac
import base64
from Crypto.Cipher import AES


def create_hmac(str_to_hmac, config):
    try:
        return hmac.new(config.cookie_key, str_to_hmac, hashlib.sha256).hexdigest()
    except Exception:
        config.logger.debug("Failed to calculate hmac")
        return False


def pbkdf2_hmac(password, salt, iterations, hash_name='sha256', dklen=None):
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
    inner.update(password.translate(TRANS_36))
    outer.update(password.translate(TRANS_5C))

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
        prev = prf(salt + struct.pack(b'>I', loop), inner, outer)
        rkey = int(binascii.hexlify(prev), 16)
        for i in xrange(iterations - 1):
            prev = prf(prev, inner, outer)
            rkey ^= int(binascii.hexlify(prev), 16)
        loop += 1
        dkey += binascii.unhexlify(hex_format_string % rkey)

    return dkey[:dklen]


def prf(msg, inner, outer):
    # PBKDF2_HMAC uses the password as key. We can re-use the same
    # digest objects and just update copies to skip initialization.
    icpy = inner.copy()
    ocpy = outer.copy()
    icpy.update(msg)
    ocpy.update(icpy.digest())
    return ocpy.digest()


def decrypt_cookie(config, raw_cookie):
    """
    Decrypting the PerimeterX risk cookie using AES
    :return: Returns decrypted value if valid and False if not
    :rtype: Bool|String
    """
    logger = config.logger
    logger.debug("PxCookie[decrypt_cookie]")
    try:
        parts = raw_cookie.split(':', 3)
        if len(parts) != 3:
            return False
        salt = base64.b64decode(parts[0])
        iterations = int(parts[1])
        if iterations < 1 or iterations > 10000:
            return False
        data = base64.b64decode(parts[2])
        dk = pbkdf2_hmac(hash_name='sha256', password=config.cookie_key, salt=salt, iterations=iterations, dklen=48)
        key = dk[:32]
        iv = dk[32:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        unpad = lambda s: s[0:-ord(s[-1])]
        plaintext = unpad(cipher.decrypt(data))
        logger.debug("PxCookie[decrypt_cookie] cookie decrypted")
        return plaintext
    except Exception, e:
        logger.error('Encryption tool encountered a problem during the decryption process: ' + str(e.message))
        return False


def decode_cookie(config, raw_cookie):
    config.logger.debug("PxCookie[decode_cookie]")
    return base64.b64decode(raw_cookie)
