import json
import unittest
import uuid

import mock
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from perimeterx import px_api
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext


class Test_PXApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'content-length': '100'}

    def enrich_custom_parameters(self, params):
        params['custom_param1'] = '1'
        params['custom_param2'] = '5'
        params['custom'] = '6'
        return params

    def test_prepare_risk_body(self):
        config = PxConfig({'app_id': 'app_id', 'enrich_custom_parameters': self.enrich_custom_parameters})
        builder = EnvironBuilder(headers=self.headers, path='/')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.s2s_call_reason = 'no_cookie'
        body = px_api.prepare_risk_body(context, config)
        self.assertEqual(body['additional'].get('custom_param1'), '1')
        self.assertEqual(body['additional'].get('custom_param2'), '5')
        self.assertFalse(body['additional'].get('custom'))

    def test_send_risk_request(self):
        config = PxConfig({'app_id': 'app_id',
                           'enrich_custom_parameters': self.enrich_custom_parameters,
                           'auth_token': 'auth'})
        builder = EnvironBuilder(headers=self.headers, path='/test_path')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        uuid_val = str(uuid.uuid4())
        response = ResponseMock({'score': 100, 'uuid': uuid_val, 'action': 'c'})
        with mock.patch('perimeterx.px_httpc.send', return_value=response):
            response = px_api.send_risk_request(context, config)
            self.assertEqual({'action': 'c', 'score': 100, 'uuid': uuid_val}, response)

    def test_verify(self):
        config = PxConfig({'app_id': 'app_id',
                           'enrich_custom_parameters': self.enrich_custom_parameters,
                           'auth_token': 'auth'})
        builder = EnvironBuilder(headers=self.headers, path='/test_path')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        uuid_val = str(uuid.uuid4())
        data_enrichment = {'timestamp': 10033200222}
        response = {'score': 100, 'uuid': uuid_val, 'action': 'c', 'data_enrichment': data_enrichment}
        with mock.patch('perimeterx.px_api.send_risk_request', return_value=response):
            api_response = px_api.verify(context, config)
            self.assertEqual('s2s_high_score', context.block_reason)
            self.assertEqual('c', context.block_action)
            self.assertTrue(api_response)
            self.assertEqual(data_enrichment, context.pxde)



class ResponseMock(object):
    def __init__(self, dict):
        self.content = json.dumps(dict)
