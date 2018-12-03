import unittest
from perimeterx import px_httpc
import requests_mock
from perimeterx.px_config import PxConfig


class TestPXHttpc(unittest.TestCase):
    def test_send(self):
        with requests_mock.mock() as m:
            config = PxConfig({'app_id': 'PXfake_app_id'})
            full_url = 'this_url.com/uri'
            method = 'POST'
            body = 'content to post'

            headers = {'content-type': 'application/json'}

            m.post('https://' + full_url)
            response = px_httpc.send(full_url=full_url, config=config,method=method,body=body,headers=headers)
            m.called
            m.get('https://' + full_url)
            method = 'GET'
            response = px_httpc.send(full_url=full_url, config=config,method=method,body=body,headers=headers)
            self.assertEqual(m.call_count, 2)