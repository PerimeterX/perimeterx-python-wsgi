from px_cookie import PxCookie
from px_constants import *


class PxTokenV3(PxCookie):

    def __init__(self, ctx, config, token):
        if token is None:
            token = ctx['px_cookies'].get(PREFIX_PX_TOKEN_V3, '')

        print("Token: " + token)
        self.ctx = ctx
        self.config = config
        spliced_cookie =token.split(":", 1)

        print ("Count: " + spliced_cookie.count)

        if spliced_cookie.count > 1:
            self.hmac = spliced_cookie[0]
            self.raw_cookie = spliced_cookie[1]

    def get_score(self):
        return self.decoded_cookie['s']

    def get_hmac(self):
        return self.hmac

    def get_action(self):
        return self.decoded_cookie['a']

    def is_cookie_format_valid(self):
        c = self.decoded_cookie;
        return 't' in c and 'v' in c and 'u' in c and 's' in c and 'a' in c

    def is_secured(self):
        return self.is_cookie_valid(self.raw_cookie)

