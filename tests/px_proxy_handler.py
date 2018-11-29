import unittest

from httplib import HTTPResponse

from perimeterx.px_proxy_handler import PXProxy
from perimeterx.px_config import PXConfig
from mock import MagicMock,patch

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

    # def test_send_reverse_client_request(self):
    #     content = 'client js content'
    #     config = PXConfig({'app_id': 'PXfake_app_id'})
    #     ctx = {'uri': '/fake_app_id/init.js', 'headers': {'X-FORWARDED-FOR': '127.0.0.1'}}
    #     fake = HttpResponse(content=content, status=200, reason='OK', content_type='text/html')
    #     px_proxy = PXProxy(config)
    #     config = PXConfig({'app_id': 'PXfake_app_id'})
    #     with patch('perimeterx.px_httpc.send_https', return_value=fake):
    #         result = px_proxy.handle_reverse_request(config=config, ctx=ctx, start_response= lambda x: x)
    #         print ''



