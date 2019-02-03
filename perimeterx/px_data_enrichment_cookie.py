import json

from perimeterx.px_cookie import PxCookie


class PxDataEnrichmentCookie(PxCookie):

    def __init__(self, config):
        super(PxDataEnrichmentCookie, self).__init__(config)
        self._is_valid = False
        self._payload = {}
        self._hmac = ''
        self._decoded_cookie = ''

    def from_raw_cookie(self, raw_cookie):
        if not raw_cookie:
            return

        spliced_cookie = raw_cookie.split(':')
        if len(spliced_cookie) != 2:
            return

        self._hmac = spliced_cookie[0]
        self._raw_cookie = spliced_cookie[1]
        self._is_valid = self.is_cookie_valid(self._raw_cookie)

        self._decoded_cookie = self.decode_cookie()
        try:
            self._payload = json.loads(self._decoded_cookie)
        except Exception as err:
            msg = 'PxDataEnrichmentCookie[__init__] failed to decode/unserialize data enrichment payload: %s' % err
            self._logger.debug(msg)

    @property
    def is_valid(self):
        return self._is_valid

    @is_valid.setter
    def is_valid(self, is_valid):
        self._is_valid = is_valid

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, payload):
        self._payload = payload
