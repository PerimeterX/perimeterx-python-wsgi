import base64
import binascii
import hashlib
import json
import struct
import sys
import traceback
from time import time

from Crypto.Cipher import AES

import px_enc_utils
from px_constants import *


class PxCookie(object):

    def __init__(self, config):
        self._config = config
        self._logger = config.logger
        self._raw_cookie = ''
        self._hmac = ''

    def build_px_cookie(self, px_cookies, user_agent=''):
        self._logger.debug("PxCookie[build_px_cookie]")
        if not px_cookies:
            self._logger.debug('Cookie is missing')
            return None

        px_cookie_keys = px_cookies.keys()
        px_cookie_keys.sort(reverse=True)
        for prefix in px_cookie_keys:
            if prefix == PREFIX_PX_TOKEN_V1 or prefix == PREFIX_PX_COOKIE_V1:
                self._logger.debug('Cookie/Token V1 found, evaluating..')
                from px_cookie_v1 import PxCookieV1
                return prefix, PxCookieV1(self._config, px_cookies[prefix])
            if prefix == PREFIX_PX_TOKEN_V3 or prefix == PREFIX_PX_COOKIE_V3:
                self._logger.debug('Cookie/Token V3 found, evaluating..')
                from px_cookie_v3 import PxCookieV3
                ua = ''
                if prefix == PREFIX_PX_COOKIE_V3:
                    ua = user_agent
                return prefix, PxCookieV3(self._config, px_cookies[prefix], ua)

        self._logger.debug('Cookie is missing')

    def decode_cookie(self):
        self._logger.debug("PxCookie[decode_cookie]")
        return px_enc_utils.decode_cookie(self._config, self._raw_cookie)

        '''
        Password based key derivation function 2 (PKCS #5 v2.0)

        This Python implementations based on the hmac module about as fast
        as OpenSSL's PKCS5_PBKDF2_HMAC for short passwords and much faster
        for long passwords.
        '''

    def pbkdf2_hmac(self, hash_name, password, salt, iterations, dklen=None):
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
        try:
            parts = self._raw_cookie.split(':', 3)
            if len(parts) != 3:
                return False
            salt = base64.b64decode(parts[0])
            iterations = int(parts[1])
            if iterations < 1 or iterations > 10000:
                return False
            data = base64.b64decode(parts[2])
            dk = self.pbkdf2_hmac('sha256', self._config.cookie_key, salt, iterations, dklen=48)
            key = dk[:32]
            iv = dk[32:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            unpad = lambda s: s[0:-ord(s[-1])]
            plaintext = unpad(cipher.decrypt(data))
            self._logger.debug('cookie decrypted')
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
            calculated_digest = px_enc_utils.create_hmac(str_to_hmac, self._config)
            return self.get_hmac() == calculated_digest
        except Exception as err:
            self._logger.debug("failed to calculate hmac: {}".format(err))
            return False

    def deserialize(self):
        logger = self._logger
        if self._config.encryption_enabled:
            cookie = px_enc_utils.decrypt_cookie(config=self._config, raw_cookie=self._raw_cookie)
        else:
            cookie = px_enc_utils.decode_cookie(config=self._config, raw_cookie=self._raw_cookie)

        if not cookie:
            return False

        logger.debug('Original token deserialized: {}'.format(cookie))
        self.decoded_cookie = json.loads(cookie)
        return self.is_cookie_format_valid()

    def is_high_score(self):
        return self.get_score() >= self._config.blocking_score

    def get_timestamp(self):
        return self.decoded_cookie['t']

    def get_uuid(self):
        return self.decoded_cookie['u']

    def get_vid(self):
        return self.decoded_cookie['v']

    def get_age(self):
        return int(round(time() * 1000)) - self.decoded_cookie['t']

    def get_hmac(self):
        return self._hmac
