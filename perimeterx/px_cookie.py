import json
from px_constants import *
from Crypto.Cipher import AES
from time import time
import base64
import hmac
import hashlib
import sys
import traceback
import binascii
import struct


class PxCookie:

    def __init__(self):
        pass

    @staticmethod
    def build_px_cookie(ctx, config):
        config["logger"].debug("PxCookie[build_px_cookie]")
        px_cookies = ctx['px_cookies'].keys()
        px_cookies.sort(reverse=True)

        # Check that its not empty
        if not px_cookies:
            return None

        prefix = px_cookies[0]
        if prefix == PREFIX_PX_COOKIE_V1:
            config["logger"].debug("PxCookie[build_px_cookie] using cookie v1")
            from px_cookie_v1 import PxCookieV1
            return PxCookieV1(ctx, config)

        if prefix == PREFIX_PX_COOKIE_V3:
            config["logger"].debug("PxCookie[build_px_cookie] using cookie v3")
            from px_cookie_v3 import PxCookieV3
            return PxCookieV3(ctx, config)

    def decode_cookie(self):
        self.config['logger'].debug("PxCookie[decode_cookie]")
        return base64.b64decode(self.raw_cookie)

    def pbkdf2_hmac(self, hash_name, password, salt, iterations, dklen=None):
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
        inner.update(password.translate(TRANS_36))
        outer.update(password.translate(TRANS_5C))

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

    def decrypt_cookie(self):
        """
        Decrypting the PerimeterX risk cookie using AES
        :return: Returns decrypted value if valid and False if not
        :rtype: Bool|String
        """
        self.config['logger'].debug("PxCookie[decrypt_cookie]")
        try:
            parts = self.raw_cookie.split(':', 3)
            if len(parts) != 3:
                return False
            salt = base64.b64decode(parts[0])
            iterations = int(parts[1])
            if iterations < 1 or iterations > 10000:
                return False
            data = base64.b64decode(parts[2])
            dk = self.pbkdf2_hmac('sha256', self.config['cookie_key'], salt, iterations, dklen=48)
            key = dk[:32]
            iv = dk[32:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            unpad = lambda s: s[0:-ord(s[-1])]
            plaintext = unpad(cipher.decrypt(data))
            self.config['logger'].debug("PxCookie[decrypt_cookie] cookie decrypted")
            return plaintext
        except:
            print traceback.format_exception(*sys.exc_info())
            return None

    def is_cookie_expired(self):
        """
        Checks if cookie validity time expired.
        :return: Returns True if valid and False if not
        :rtype: Bool
        """
        now = int(round(time() * 1000))
        expire = self.get_timestamp()
        return now > expire

    def is_cookie_valid(self, str_to_hmac):
        """
        Checks if cookie hmac signing match the request.
        :return: Returns True if valid and False if not
        :rtype: Bool
        """
        try:
            calculated_digest = hmac.new(self.config['cookie_key'], str_to_hmac, hashlib.sha256).hexdigest()
            return self.get_hmac() == calculated_digest
        except:
            self.config["logger"].debug("failed to calculate hmac")
            return False

    def deserialize(self):
        self.config['logger'].debug("PxCookie[deserialize]")
        if self.config.get("encryption_enabled", False):
            cookie = self.decrypt_cookie()
        else:
            cookie = self.decode_cookie()

        if not cookie:
            return False

        self.config['logger'].debug("PxCookie[deserialize] decoded cookie: " + cookie)
        self.decoded_cookie = json.loads(cookie)
        return self.is_cookie_format_valid()

    def is_high_score(self):
        return self.get_score() >= self.config['blocking_score']

    def get_timestamp(self):
        return self.decoded_cookie['t']

    def get_uuid(self):
        return self.decoded_cookie['u']

    def get_vid(self):
        return self.decoded_cookie['v']




