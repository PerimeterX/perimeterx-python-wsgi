import unittest
from perimeterx.px_data_enrichment_cookie import PxDataEnrichmentCookie
from perimeterx.px_config import PxConfig
import base64
import json
import hmac
import hashlib


class TestPXDataEnrichmentCookie(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = PxConfig({'app_id': 'fake_app_id', 'cookie_key': 'test_key'})
        cls.config = config

    def test_from_raw_cookie(self):
        data_enrichment_cookie = PxDataEnrichmentCookie(self.config)
        data = {'timestamp': 1398239283293}
        data_json_string = json.dumps(data)
        encoded_data = base64.b64encode(data_json_string)
        hmac_hex = hmac.new(self.config.cookie_key, encoded_data, hashlib.sha256).hexdigest()
        raw_cookie = hmac_hex + ':' + encoded_data
        data_enrichment_cookie.from_raw_cookie(raw_cookie)
        self.assertEqual(data_enrichment_cookie.payload, data)
        self.assertTrue(data_enrichment_cookie.is_valid)
