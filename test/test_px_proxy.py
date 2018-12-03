import unittest
import requests_mock
from perimeterx.px_proxy import PXProxy
from perimeterx.px_config import PxConfig
from perimeterx import px_constants
from perimeterx.px_context import PxContext


class Test_PXProxy(unittest.TestCase):

    def test_should_reverse_request(self):
        config = PxConfig({'app_id': 'PXfake_app_id'})
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
        config = PxConfig({'app_id': 'PXfake_app_id'})
        ctx = PxContext({'PATH_INFO': '/fake_app_id/init.js',
                         'HTTP_X_FORWARDED_FOR': '127.0.0.1',
                         'ip': '127.0.0.1'},
                        config)
        headers = {'host': px_constants.CLIENT_HOST,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: ctx.ip,
                   px_constants.FIRST_PARTY_FORWARDED_FOR: '127.0.0.1'}
        mock.get(url='https://client.perimeterx.net/PXfake_app_id/main.min.js', text=content, request_headers=headers,
                 status_code=200, reason='OK')
        px_proxy = PXProxy(config)
        response_body = px_proxy.handle_reverse_request(config=config, ctx=ctx, start_response=lambda x, y: x, body='')
        self.assertEqual(content, response_body)

    @requests_mock.mock()
    def test_send_reverse_captcha_request(self, mock):
        content = 'captcha js content'
        config = PxConfig({'app_id': 'PXfake_app_id'})
        ctx = PxContext({'PATH_INFO': '/fake_app_id/captcha/captcha.js',
                         'HTTP_X_FORWARDED_FOR': '127.0.0.1',
                         'ip': '127.0.0.1',
                         'QUERY_STRING': 'a=c&amp;u=cfe74220-f484-11e8-9b14-d7280325a290&amp;v=0701bb80-f482-11e8-8a31-a37cf9620569&amp;m=0'},
                        PxConfig({'app_id': 'fake_app_id'}))
        headers = {'host': px_constants.CAPTCHA_HOST,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: ctx.ip,
                   px_constants.FIRST_PARTY_FORWARDED_FOR: '127.0.0.1'}
        mock.get(
            url='https://captcha.px-cdn.net/PXfake_app_id/captcha.js?a=c&amp;u=cfe74220-f484-11e8-9b14-d7280325a290&amp;v=0701bb80-f482-11e8-8a31-a37cf9620569&amp;m=0',
            text=content, request_headers=headers, status_code=200, reason='OK')
        px_proxy = PXProxy(config)
        response_body = px_proxy.handle_reverse_request(config=config, ctx=ctx, start_response=lambda x, y: x, body='')
        self.assertEqual(content, response_body)

    @requests_mock.mock()
    def test_send_reverse_xhr_request(self, mock):
        content = 'captcha content'
        config = PxConfig({'app_id': 'PXfake_app_id'})
        ctx = PxContext({'PATH_INFO': '/fake_app_id/xhr/api/v1/collector',
                         'HTTP_X_FORWARDED_FOR': '127.0.0.1',
                         'ip': '127.0.0.1'},
                        PxConfig({'app_id': 'fake_app_id'}))
        headers = {'host': config.collector_host,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: ctx.ip,
                   px_constants.FIRST_PARTY_FORWARDED_FOR: '127.0.0.1'}
        mock.post(url='https://collector-pxfake_app_id.perimeterx.net/api/v1/collector', text=content,
                  request_headers=headers, status_code=200, reason='OK')
        px_proxy = PXProxy(config)
        response_body = px_proxy.handle_reverse_request(config=config, ctx=ctx, start_response=lambda x, y: x, body='')
        self.assertEqual(content, response_body)
