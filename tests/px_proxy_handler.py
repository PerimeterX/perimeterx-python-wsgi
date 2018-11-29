import unittest
import requests
import requests_mock
from perimeterx.px_proxy_handler import PXProxy
from perimeterx.px_config import PXConfig
from perimeterx import px_constants
class Test_PXProxy(unittest.TestCase):

    def test_should_reverse_request(self):
        config = PXConfig({'app_id': 'PXfake_app_id'})
        px_proxy = PXProxy(config)
        should_reverse = px_proxy.should_reverse_request('/fake_app_id/init.js')
        self.assertTrue(should_reverse)
        should_reverse = px_proxy.should_reverse_request('/fake_app_id/xhr')
        self.assertTrue(should_reverse)
        should_reverse = px_proxy.should_reverse_request('/fake_app_id/captcha')
        self.assertTrue(should_reverse)

    @requests_mock.mock()
    def test_send_reverse_client_request(self, mock):
        content = 'client js content'
        config = PXConfig({'app_id': 'PXfake_app_id'})
        ctx = {'uri': '/fake_app_id/init.js', 'headers': {'X-FORWARDED-FOR': '127.0.0.1'}, 'ip': '127.0.0.1'}
        headers = {'host': px_constants.CLIENT_HOST,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: ctx.get('ip'),
                   px_constants.FIRST_PARTY_FORWARDED_FOR: '127.0.0.1'}
        mock.get(url='https://client.perimeterx.net/PXfake_app_id/main.min.js', text=content, request_headers= headers, status_code=200, reason='OK')
        px_proxy = PXProxy(config)
        config = PXConfig({'app_id': 'PXfake_app_id'})
        response_body = px_proxy.handle_reverse_request(config=config, ctx=ctx, start_response= lambda x, y: x, body='')
        self.assertEqual(content, response_body)

    @requests_mock.mock()
    def test_send_reverse_captcha_request(self, mock):
        content = 'captcha js content'
        config = PXConfig({'app_id': 'PXfake_app_id'})
        ctx = {'uri': '/fake_app_id/init.js', 'headers': {'X-FORWARDED-FOR': '127.0.0.1'}, 'ip': '127.0.0.1'}
        headers = {'host': px_constants.CAPTCHA_HOST,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: ctx.get('ip'),
                   px_constants.FIRST_PARTY_FORWARDED_FOR: '127.0.0.1'}
        mock.get(url='https://client.perimeterx.net/PXfake_app_id/main.min.js', text=content, request_headers= headers, status_code=200, reason='OK')
        px_proxy = PXProxy(config)
        config = PXConfig({'app_id': 'PXfake_app_id'})
        response_body = px_proxy.handle_reverse_request(config=config, ctx=ctx, start_response= lambda x, y: x, body='')
        self.assertEqual(content, response_body)



