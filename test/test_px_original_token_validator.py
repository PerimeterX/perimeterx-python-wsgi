import unittest
from perimeterx import px_original_token_validator
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext
from perimeterx import px_constants
from werkzeug.wrappers import Request
from werkzeug.test import EnvironBuilder


class TestPXOriginalTokenValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cookie_key = 'Pyth0nS3crE7K3Y'
        cls.config = PxConfig({'app_id': 'app_id',
                               'cookie_key': cls.cookie_key})
        cls.headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'content_length': '100',
                       'path': '/fake_app_id/init.js'}

    def test_verify(self):
        self.headers[
            px_constants.MOBILE_SDK_ORIGINAL_HEADER] = '3:bd078865fa9627f626d6f7d6828ab595028d2c0974065ab6f6c5a9f80c4593cd:OCIluokZHHvqrWyu8zrWSH8Vu7AefCjrd4CMx/NXsX58LzeV40EZIlPG4gsNMoAYzH88s/GoZwv+DpQa76C21A==:1000:zwT+Rht/YGDNWKkzHtJAB7IiI00u4fOePL/3xWMs1nZ93lzW1XvAMGR2hLlHBmOv8O0CpylEQOZZTK1uQMls6O28Y8aQnTo5DETLkrbhpwCVeNjOcf8GVKTckITwuHfXbEcfHbdtb68s1+jHv1+vt/w/6HZqTzanaIsvFVp8vmA='
        self.headers[px_constants.MOBILE_SDK_HEADER] = '2'
        builder = EnvironBuilder(headers=self.headers)

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        verified = px_original_token_validator.verify(context, self.config)
        self.assertTrue(verified)
        self.assertEqual(context.vid, 'ce305f10-f17e-11e8-90f2-e7a14f96c498')
        self.assertEqual(context.decoded_original_token,
                         {'a': 'a', 's': 0, 'u': 'ce308620-f17e-11e8-90f2-e7a14f96c498', 't': 1663653730456,
                          'v': 'ce305f10-f17e-11e8-90f2-e7a14f96c498'})
        self.assertEqual(context.original_uuid, 'ce308620-f17e-11e8-90f2-e7a14f96c498')
        self.assertEqual(context.original_token_error, '')

    def test_decryption_error_token(self):
        self.headers[
            px_constants.MOBILE_SDK_ORIGINAL_HEADER] = '3:bd078865fa9627f626d6f7d6828ab595028d2c0974065ab6f6c5a9f80c4593cd:OCIluokZHHvqrWyu8zrWSH8Vu7AefCjrd4CMx/NXsX58LzeV40EZIlPG4gsNMoAYzH88s/GoZwv+DpQa76C21A==:1000:zwT+Rht/YGDNWKkzHtJAB7IiI00asfafu4fOePL/3xWMs1nZ93lzW1XvAMGR2hLlHBmOv8O0CpylEQOZZTK1uQMls6O28Y8aQnTo5DETLkrbhpwCVeNjOcf8GVKTckITwuHfXbEcfHbdtb68s1+jHv1+vt/w/6HZqTzanaIsvFVp8vmA='
        self.headers[px_constants.MOBILE_SDK_HEADER] = '2'
        builder = EnvironBuilder(headers=self.headers)
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        verified = px_original_token_validator.verify(context, self.config)
        self.assertFalse(verified)
        self.assertEqual(context.original_token_error, 'decryption_failed')

    def test_validation_error_token(self):
        self.headers[
            px_constants.MOBILE_SDK_ORIGINAL_HEADER] = '3:bd078865fa9627f626d6f7d6828ab595028d2c0974ds065ab6f6c5afsaa9f80c4593cd:OCIluokZHHvqrWyu8zrWSH8Vu7AefCjrd4CMx/NXsX58LzeV40EZIlPG4gsNMoAYzH88s/GoZwv+DpQa76C21A==:1000:zwT+Rht/YGDNWKkzHtJAB7IiI00u4fOePL/3xWMs1nZ93lzW1XvAMGR2hLlHBmOv8O0CpylEQOZZTK1uQMls6O28Y8aQnTo5DETLkrbhpwCVeNjOcf8GVKTckITwuHfXbEcfHbdtb68s1+jHv1+vt/w/6HZqTzanaIsvFVp8vmA='
        self.headers[px_constants.MOBILE_SDK_HEADER] = '2'
        builder = EnvironBuilder(headers=self.headers)
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        verified = px_original_token_validator.verify(context, self.config)
        self.assertFalse(verified)
        self.assertEqual(context.original_token_error, 'validation_failed')
