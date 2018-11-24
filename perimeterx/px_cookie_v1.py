from px_cookie import PxCookie
from px_constants import *


class PxCookieV1(PxCookie):

    def __init__(self, ctx, config):
        self._ctx = ctx
        self._config = config
        self.raw_cookie = ctx['px_cookies'].get(PREFIX_PX_COOKIE_V1, '')

    def get_score(self):
        return self.decoded_cookie['s']['b']

    def get_hmac(self):
        return self.decoded_cookie['h']

    def get_action(self):
        return 'c'

    def is_cookie_format_valid(self):
        c = self.decoded_cookie
        return 't' in c and 'v' in c and 'u' in c and "s" in c and 'a' in c['s'] and 'h' in c

    def is_secured(self):
        c = self.decoded_cookie
        user_agent = self._ctx.get('user_agent', '')
        ip = self._ctx.get('ip', '')
        base_hmac = str(self.get_timestamp()) + str(c['s']['a']) + str(self.get_score()) + self.get_uuid() + self.get_vid()
        hmac_with_ip = base_hmac + ip + user_agent
        hmac_without_ip = base_hmac + user_agent

        return self.is_cookie_valid(hmac_without_ip) or self.is_cookie_valid(hmac_with_ip)


