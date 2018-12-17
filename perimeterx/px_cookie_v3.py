from px_cookie import PxCookie


class PxCookieV3(PxCookie):

    def __init__(self, config, cookie, user_agent):
        super(PxCookieV3, self).__init__(config)
        self._config = config
        self._logger = config.logger
        self._user_agent = user_agent
        spliced_cookie = cookie.split(':')
        if len(spliced_cookie) is 4:
            self._hmac = spliced_cookie[0]
            self._raw_cookie = ':'.join(spliced_cookie[1:])
        else:
            self._raw_cookie = cookie

    def get_score(self):
        return self.decoded_cookie['s']

    def get_hmac(self):
        return self._hmac

    def get_action(self):
        return self.decoded_cookie['a']

    def is_cookie_format_valid(self):
        c = self.decoded_cookie
        return 't' in c and 'v' in c and 'u' in c and 's' in c and 'a' in c

    def is_secured(self):
        user_agent = self._user_agent
        str_hmac = self._raw_cookie + user_agent
        return self.is_cookie_valid(str_hmac)
