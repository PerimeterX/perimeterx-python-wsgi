from px_cookie import PxCookie


class PxCookieV3(PxCookie):

    def __init__(self, config, cookie, user_agent):
        self._config = config
        self._logger = config.logger
        self._user_agent = user_agent
        spliced_cookie = cookie.split(':')
        if len(spliced_cookie) is 4:
            self.hmac = spliced_cookie[0]
            self.raw_cookie = ':'.join(spliced_cookie[1:])
        else:
            self.raw_cookie = cookie

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
        user_agent = self._user_agent
        str_hmac = self.raw_cookie + user_agent
        return self.is_cookie_valid(str_hmac)

