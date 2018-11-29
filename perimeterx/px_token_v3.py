from px_cookie import PxCookie
from px_constants import *


class PxTokenV3(PxCookie):

    def __init__(self, config, token):

        self._config = config
        self._logger = config.logger
        spliced_cookie = token.split(":", 1)

        print ("Count: " + str(len(spliced_cookie)))

        if len(spliced_cookie) > 1:
            self.hmac = spliced_cookie[0]
            self.raw_cookie = spliced_cookie[1]
        else:
            self.raw_cookie = token


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

