import unittest

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from perimeterx import px_constants
from perimeterx import px_utils
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext


class Test_PXUtils(unittest.TestCase):

    def test_merge_two_dicts(self):
        dict1 = {'a': '1'}
        dict2 = {'b': '2'}
        merged_dict = px_utils.merge_two_dicts(dict1, dict2)
        self.assertDictEqual(merged_dict, {'a': '1', 'b': '2'})

    def test_handle_proxy_headers(self):
        headers_sample = {'ddd': 'not_proxy_url', px_constants.FIRST_PARTY_FORWARDED_FOR: 'proxy_url'}
        headers_sample = px_utils.handle_proxy_headers(headers_sample, '127.0.0.1', False)
        self.assertEqual(headers_sample[px_constants.FIRST_PARTY_FORWARDED_FOR], '127.0.0.1')
        headers_sample = {'ddd': 'not_proxy_url'}
        headers_sample = px_utils.handle_proxy_headers(headers_sample, '127.0.0.1', False)
        self.assertEqual(headers_sample[px_constants.FIRST_PARTY_FORWARDED_FOR], '127.0.0.1')

    def test_is_static_file(self):
        config = PxConfig({'app_id' : 'fake_app_id'})
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100',
                   'cookie': '_px3=bd078865fa9627f626d6f7d6828ab595028d2c0974065ab6f6c5a9f80c4593cd:OCIluokZHHvqrWyu8zrWSH8Vu7AefCjrd4CMx/NXsX58LzeV40EZIlPG4gsNMoAYzH88s/GoZwv+DpQa76C21A==:1000:zwT+Rht/YGDNWKkzHtJAB7IiI00u4fOePL/3xWMs1nZ93lzW1XvAMGR2hLlHBmOv8O0CpylEQOZZTK1uQMls6O28Y8aQnTo5DETLkrbhpwCVeNjOcf8GVKTckITwuHfXbEcfHbdtb68s1+jHv1+vt/w/6HZqTzanaIsvFVp8vmA='}
        builder = EnvironBuilder(headers=headers, path='/sample.css')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        self.assertTrue(px_utils.is_static_file(context))
        builder = EnvironBuilder(headers=headers, path='/sample.html')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        self.assertFalse(px_utils.is_static_file(context))

    def enrich_custom_parameters(self, params):
        params['custom_param1'] = '1'
        params['custom_param2'] = '2'
        params['custom'] = '6'
        params['custom_param10'] = '10'
        return params

    def test_prepare_risk_body(self):
        config = PxConfig({'app_id': 'app_id', 'enrich_custom_parameters': self.enrich_custom_parameters})
        additional = {}

        px_utils.prepare_custom_params(config, additional)
        self.assertEqual(additional.get('custom_param1'), '1')
        self.assertEqual(additional.get('custom_param2'), '2')
        self.assertEqual(additional.get('custom_param10'), '10')
        self.assertFalse(additional.get('custom_param11'))
        self.assertFalse(additional.get('custom'))
