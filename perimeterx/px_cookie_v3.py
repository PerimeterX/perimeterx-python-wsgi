from px_cookie import PxCookie
from px_constants import *


class PxCookieV3(PxCookie):

    def __init__(self, ctx, config):
        self._config = config
        self._logger = config.logger
        self._ctx = ctx
        self.raw_cookie = ''
        spliced_cookie = self._ctx['px_cookies'].get(PREFIX_PX_COOKIE_V3, '').split(":", 1)
        if len(spliced_cookie) > 1:
            self.hmac = spliced_cookie[0]
            self.raw_cookie = spliced_cookie[1]

    def get_score(self):
        return self.decoded_cookie['s']

    def get_hmac(self):
        return self.hmac

    def get_action(self):
        return self.decoded_cookie['a']

    def is_cookie_format_valid(self):
        c = self.decoded_cookie
        return 't' in c and 'v' in c and 'u' in c and 's' in c and 'a' in c

    def is_secured(self):
        user_agent = self._ctx.get('user_agent', '')
        str_hmac = self.raw_cookie + user_agent
        return self.is_cookie_valid(str_hmac)

