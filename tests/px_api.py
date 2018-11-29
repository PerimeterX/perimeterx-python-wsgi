import unittest
from perimeterx import px_api
from perimeterx.px_config import PXConfig

class Test_PXApi(unittest.TestCase):

    def enrich_custom_parameters(self, params):
        params['custom_param1'] = '1'
        params['custom_param2'] = '5'
        params['custom'] = '6'
        return params

    def test_prepare_risk_body(self):
        config = PXConfig({'app_id': 'app_id', 'enrich_custom_parameters': self.enrich_custom_parameters})
        ctx = {'headers': {}, 's2s_call_reason': 'no_cookie'}
        body = px_api.prepare_risk_body(ctx, config)
        self.assertEqual(body['additional'].get('custom_param1'), '1')
        self.assertEqual(body['additional'].get('custom_param2'), '5')
        self.assertFalse(body['additional'].get('custom'))
        print
