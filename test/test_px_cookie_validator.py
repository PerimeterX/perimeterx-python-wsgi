import unittest

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from perimeterx import px_cookie_validator
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext


class Test_PXCookieValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cookie_key = 'Pyth0nS3crE7K3Y'
        cls.config = PxConfig({'app_id': 'app_id',
                           'cookie_key': cls.cookie_key})
        cls.headers = {'X-FORWARDED-FOR': '127.0.0.1',
                    'remote-addr': '127.0.0.1',
                   'content_length': '100',
                   'path': '/fake_app_id/init.js'}

    def test_verify_no_cookie(self):
        config = self.config

        builder = EnvironBuilder(headers= self.headers)

        env = builder.get_environ()
        request = Request(env)
        ctx = PxContext(request, PxConfig({'app_id': 'fake_app_id'}))
        verified = px_cookie_validator.verify(ctx, config)
        self.assertFalse(verified)
        self.assertEqual('no_cookie', ctx.s2s_call_reason)

    def test_verify_valid_cookie(self):
        config = self.config
        self.headers['cookie'] = '_px3=bd078865fa9627f626d6f7d6828ab595028d2c0974065ab6f6c5a9f80c4593cd:OCIluokZHHvqrWyu8zrWSH8Vu7AefCjrd4CMx/NXsX58LzeV40EZIlPG4gsNMoAYzH88s/GoZwv+DpQa76C21A==:1000:zwT+Rht/YGDNWKkzHtJAB7IiI00u4fOePL/3xWMs1nZ93lzW1XvAMGR2hLlHBmOv8O0CpylEQOZZTK1uQMls6O28Y8aQnTo5DETLkrbhpwCVeNjOcf8GVKTckITwuHfXbEcfHbdtb68s1+jHv1+vt/w/6HZqTzanaIsvFVp8vmA='
        builder = EnvironBuilder(headers=self.headers)

        env = builder.get_environ()
        request = Request(env)
        ctx = PxContext(request, PxConfig({'app_id': 'fake_app_id'}))
        verified = px_cookie_validator.verify(ctx, config)
        self.assertTrue(verified)
        self.assertEqual('none', ctx.s2s_call_reason)
        del self.headers['cookie']

    def test_verify_decryption_failed(self):
        config = self.config
        cookie_value = '774958bcc233ea1a876b92ababf47086d8a4d95165bbd6f98b55d7e61afd2a05:ow3Er5dskpt8ZZ11CRiDMAueEi3ozJTqMBnYzsSM7/8vHTDA0so6ekhruiTrXa/taZINotR5PnTo78D5zM2pWw==:1000:uQ3Tdt7D3mSO5CuHDis3GgrnkGMC+XAghbHuNOE9x4H57RAmtxkTcNQ1DaqL8rx79bHl0iPVYlOcRmRgDiBCUoizBdUCjsSIplofPBLIl8WpfHDDtpxPKzz9I2rUEbFgfhFjiTY3rPGob2PUvTsDXTfPUeHnzKqbNTO8z7H6irFnUE='
        self.headers['cookie'] = '_px3=' + cookie_value
        builder = EnvironBuilder(headers=self.headers)
        env = builder.get_environ()
        request = Request(env)
        ctx = PxContext(request, PxConfig({'app_id': 'fake_app_id'}))
        verified = px_cookie_validator.verify(ctx, config)
        self.assertFalse(verified)
        self.assertEqual('cookie_decryption_failed', ctx.s2s_call_reason)
        self.assertEqual('_px3=' + cookie_value, ctx.px_cookie_raw)
        del self.headers['cookie']

    def test_verify_cookie_high_score(self):
        config = self.config
        self.headers['cookie'] = '_px3=bf46ceff75278ae166f376cbf741a7639060581035dd4e93641892c905dd0d67:EGFGcwQ2rum7KRmQCeSXBAUt1+25mj2DFJYi7KJkEliF3cBspdXtD2X03Csv8N8B6S5Bte/4ccCcETkBNDVxTw==:1000:x9x+oI6BISFhlKEERpf8HpZD2zXBCW9lzVfuRURHaAnbaMnpii+XjPEd7a7EGGUSMch5ramy3y+KOxyuX3F+LbGYwvn3OJb+u40zU+ixT1w5N15QltX+nBMhC7izC1l8QtgMuG/f3Nts5ebnec9j2V7LS5Y1/5b73rd9s7AMnug='
        builder = EnvironBuilder(headers=self.headers)
        env = builder.get_environ()
        request = Request(env)
        ctx = PxContext(request, PxConfig({'app_id': 'fake_app_id'}))
        verified = px_cookie_validator.verify(ctx, config)
        self.assertTrue(verified)
        self.assertEqual('none', ctx.s2s_call_reason)
        del self.headers['cookie']

    def test_verify_hmac_validation(self):
        config = self.config
        cookie_value = '774958bcc232343ea1a876b92ababf47086d8a4d95165bbd6f98b55d7e61afd2a05:ow3Er5dskpt8ZZ11CRiDMAueEi3ozJTqMBnYzsSM7/8vHTDA0so6ekhruiTrXa/taZINotR5PnTo78D5zM2pWw==:1000:uQ3Tdt7D3mSO5CuHDis3GgrnkGMC+XAghbHuNOE9x4H57RAmtxkTcNQ1DaqL8rx79bHl0iPVYlOcRmRgDiBCUoizBdUCjsSIplofPBLIl8WpfHDDtpxPKzz9I2rUEbFFjiTY3rPGob2PUvTsDXTfPUeHnzKqbNTO8z7H6irFnUE='
        self.headers['cookie'] = '_px3=' + cookie_value
        builder = EnvironBuilder(headers=self.headers)
        env = builder.get_environ()
        request = Request(env)
        ctx = PxContext(request, PxConfig({'app_id': 'fake_app_id'}))
        verified = px_cookie_validator.verify(ctx, config)
        self.assertFalse(verified)
        self.assertEqual('cookie_validation_failed', ctx.s2s_call_reason)
        self.assertEqual('', ctx.px_cookie_raw)
        del self.headers['cookie']

    def test_verify_expired_cookie(self):
        config = self.config
        cookie_value = '0d67bdf4a58c524b55b9cf0f703e4f0f3cbe23a10bd2671530d3c7e0cfa509eb:HOiYSw11ICB2A+HYx+C+l5Naxcl7hMeEo67QNghCQByyHlhWZT571ZKfqV98JFWg7TvbV9QtlrQtXakPYeIEjQ==:1000:+kuXS/iJUoEqrm8Fo4K0cTebsc4YQZu+f5bRGX0lC1T+l0g1gzRUuKiCtWTar28Y0wjch1ZQvkNy523Pxr07agVi/RL0SUktmEl59qGor+m4FLewZBVdcgx/Ya9kU0riis98AAR0zdTpTtoN5wpNbmztIpOZ0YejeD0Esk3vagU='
        self.headers['cookie'] = '_px3=' + cookie_value
        builder = EnvironBuilder(headers=self.headers)
        env = builder.get_environ()
        request = Request(env)
        ctx = PxContext(request, PxConfig({'app_id': 'fake_app_id'}))
        verified = px_cookie_validator.verify(ctx, config)
        self.assertFalse(verified)
        self.assertEqual('cookie_expired', ctx.s2s_call_reason)
        self.assertEqual('', ctx.px_cookie_raw)
        del self.headers['cookie']

    def test_cookie_decryption_failed_px_cookie_raw(self):
        config = self.config
        false_cookie = '_px3=774958bcc233ea1a876b92ababf47086d8a4d95165bbd6f98b55d7e61afd2a05:ow3Er5dskpt8ZZ11CRiDMAueEi3ozJTqMBnYzsSM7/8vHTDA0so6ekhruiTrXa/taZINotR5PnTo78D5zM2pWw==:1000:uQ3Tdt7D3mSO5CuHDis3GgrnkGMC+XAghbHuNOE9x4H57RAmtxkTcNQ1DaqL8rx79bHl0iPVYlOcRmRgDiBCUoizBdUCjsSIplofPBLIl8WpfHDDtpxPKzz9I2rUEbFgfhFjiTY3rPGob2PUvTsDXTfPUeHnzKqbNTO8z7H6irFnUE='
        self.headers['cookie'] = false_cookie
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')
        env = builder.get_environ()
        request = Request(env)
        ctx = PxContext(request, config)
        verified = px_cookie_validator.verify(ctx, config)
        self.assertEqual(ctx.px_cookie_raw, false_cookie)
        del self.headers['cookie']





