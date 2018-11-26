from perimeterx import px_httpc
import unittest
from mock import MagicMock,patch
from perimeterx.px_config import PXConfig
import httplib


class Test_PXHTTPC(unittest.TestCase):

    def test_send(self):
        # px_config = PXConfig({'app_id': 'fake_app_id',
        #                       'auth_token': 'fake_auth_token'})
        # http_client = httplib.HTTPConnection(host='host', timeout=1)
        # from httplib2 import Response
        # http_client.request = MagicMock(return_value= Response({'status':'200'}))
        # with patch('perimeterx.px_httpc.httplib', return_value=http_client):
        #     message = px_httpc.send('uri', 'body', px_config)


        print 'f'