import unittest
from perimeterx import px_api
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext
import mock
import uuid
import json

class Test_PXApi(unittest.TestCase):



    def enrich_custom_parameters(self, params):
        params['custom_param1'] = '1'
        params['custom_param2'] = '5'
        params['custom'] = '6'
        return params

    def test_prepare_risk_body(self):
        config = PxConfig({'app_id': 'app_id', 'enrich_custom_parameters': self.enrich_custom_parameters})
        ctx = PxContext({},config)
        ctx.s2s_call_reason = 'no_cookie'
        body = px_api.prepare_risk_body(ctx, config)
        self.assertEqual(body['additional'].get('custom_param1'), '1')
        self.assertEqual(body['additional'].get('custom_param2'), '5')
        self.assertFalse(body['additional'].get('custom'))

    def test_send_risk_request(self):
        config = PxConfig({'app_id': 'app_id',
                           'enrich_custom_parameters': self.enrich_custom_parameters,
                           'auth_token': 'auth'})
        ctx = PxContext({'PATH_INFO': '/test_path'}, config)
        uuid_val = str(uuid.uuid4())
        response = ResponseMock({'score': 100, 'uuid': uuid_val, 'action': 'c'})
        with mock.patch('perimeterx.px_httpc.send', return_value=response):
            response = px_api.send_risk_request(ctx, config)
            self.assertEqual({'action': 'c', 'score': 100, 'uuid': uuid_val}, response)



class ResponseMock(object):
    def __init__(self, dict):
        self.content = json.dumps(dict)

