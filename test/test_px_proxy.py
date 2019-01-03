import unittest

import requests_mock
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from perimeterx import px_constants
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext
from perimeterx.px_proxy import PxProxy


class Test_PXProxy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = PxConfig({'app_id': 'PXfake_app_id'})
        cls.headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'content_length': '100'}


    def test_should_reverse_request(self):
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        px_proxy = PxProxy(self.config)

        should_reverse = px_proxy.should_reverse_request(context.uri)
        self.assertTrue(should_reverse)
        should_reverse = px_proxy.should_reverse_request(context.uri)
        self.assertTrue(should_reverse)
        should_reverse = px_proxy.should_reverse_request(context.uri)
        self.assertTrue(should_reverse)

    @requests_mock.mock()
    def test_send_reverse_client_request(self, mock):
        content = 'client js content'
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        headers = {'host': px_constants.CLIENT_HOST,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: context.ip,
                   px_constants.FIRST_PARTY_FORWARDED_FOR: '127.0.0.1'}
        mock.get(url='https://client.perimeterx.net/PXfake_app_id/main.min.js', text=content, request_headers=headers,
                 status_code=200, reason='OK')
        px_proxy = PxProxy(self.config)
        status, headers, body = px_proxy.send_reverse_client_request(config=self.config, ctx=context)
        self.assertEqual(content, body)

    @requests_mock.mock()
    def test_send_reverse_captcha_request(self, mock):
        content = 'captcha js content'
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/captcha/captcha.js', query_string='a=c&amp;u=cfe74220-f484-11e8-9b14-d7280325a290&amp;v=0701bb80-f482-11e8-8a31-a37cf9620569&amp;m=0')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        headers = {'host': px_constants.CAPTCHA_HOST,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: context.ip,
                   px_constants.FIRST_PARTY_FORWARDED_FOR: '127.0.0.1'}
        mock.get(
            url='https://captcha.px-cdn.net/PXfake_app_id/captcha.js?a=c&amp;u=cfe74220-f484-11e8-9b14-d7280325a290&amp;v=0701bb80-f482-11e8-8a31-a37cf9620569&amp;m=0',
            text=content, request_headers=headers, status_code=200, reason='OK')
        px_proxy = PxProxy(self.config)
        status, headers, body = px_proxy.send_reverse_captcha_request(config=self.config, ctx=context)
        self.assertEqual(content, body)

    @requests_mock.mock()
    def test_send_reverse_xhr_request(self, mock):
        content = 'xhr content'
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/xhr/api/v1/collector', method='POST')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)

        headers = {'host': self.config.collector_host,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: context.ip,
                   px_constants.FIRST_PARTY_FORWARDED_FOR: '127.0.0.1'}
        mock.post(url='https://collector-pxfake_app_id.perimeterx.net/api/v1/collector', text=content,
                  request_headers=headers, status_code=200, reason='OK')
        px_proxy = PxProxy(self.config)
        status, headers, body = px_proxy.send_reverse_xhr_request(config=self.config, ctx=context, body=content)
        self.assertEqual(content, body)
