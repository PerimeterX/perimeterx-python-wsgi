from perimeterx import px_utils
import unittest
from perimeterx import px_constants


class Test_PXUtils(unittest.TestCase):

    def test_merge_two_dicts(self):
        dict1 = {'a': '1'}
        dict2 = {'b': '2'}
        merged_dict = px_utils.merge_two_dicts(dict1, dict2)
        self.assertDictEqual(merged_dict, {'a': '1', 'b': '2'})

    def test_handle_proxy_headers(self):
        headers_sample = {'ddd': 'not_proxy_url', px_constants.FIRST_PARTY_FORWARDED_FOR: 'proxy_url'}
        headers_sample = px_utils.handle_proxy_headers(headers_sample, '127.0.0.1')
        self.assertEqual(headers_sample[px_constants.FIRST_PARTY_FORWARDED_FOR], '127.0.0.1')
        headers_sample = {'ddd': 'not_proxy_url'}
        headers_sample = px_utils.handle_proxy_headers(headers_sample, '127.0.0.1')
        self.assertEqual(headers_sample[px_constants.FIRST_PARTY_FORWARDED_FOR], '127.0.0.1')

    def test_is_static_file(self):
        ctx = {'uri': '/sample.css'}
        self.assertTrue(px_utils.is_static_file(ctx))
        ctx = {'uri': '/sample.html'}
        self.assertFalse(px_utils.is_static_file(ctx))
