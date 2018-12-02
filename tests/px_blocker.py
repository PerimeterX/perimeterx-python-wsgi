from perimeterx.px_blocker import PXBlocker

import os
import unittest
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext


class Test_PXBlocker(unittest.TestCase):

    def test_is_json_response(self):
        px_blocker = PXBlocker()
        config = PxConfig({'app_id': 'PXfake_app_id'})
        ctx = PxContext({'PATH_INFO': '/fake_app_id/init.js',
                         'HTTP_X_FORWARDED_FOR': '127.0.0.1',
                         'ip': '127.0.0.1',
                         'HTTP_ACCEPT': 'text/html'},
                        config)

        self.assertFalse(px_blocker.is_json_response(ctx))
        ctx.headers['Accept'] = 'application/json'
        self.assertTrue(px_blocker.is_json_response(ctx))

    def test_handle_blocking(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'

        config = PxConfig({'app_id': 'PXfake_app_id'})
        ctx = PxContext({'PATH_INFO': '/fake_app_id/init.js',
                         'HTTP_X_FORWARDED_FOR': '127.0.0.1',
                         'ip': '127.0.0.1',
                         'HTTP_ACCEPT': 'text/html'},
                        config)
        ctx.vid = vid
        ctx.uuid = px_uuid
        px_config = PxConfig({'app_id': 'PXfake_app_ip'})
        message, _, _ = px_blocker.handle_blocking(ctx, px_config)
        working_dir = os.path.dirname(os.path.realpath(__file__))
        with open(working_dir + '/px_blocking_messages/blocking.txt', 'r') as myfile:
            blocking_message = myfile.read()

        self.assertEqual(message, blocking_message)

    def test_handle_ratelimit(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        config = PxConfig({'app_id': 'PXfake_app_id'})
        ctx = PxContext({'PATH_INFO': '/fake_app_id/init.js',
                         'HTTP_X_FORWARDED_FOR': '127.0.0.1',
                         'ip': '127.0.0.1',
                         'HTTP_ACCEPT': 'text/html'},
                        config)
        ctx.vid = vid
        ctx.uuid = px_uuid
        ctx.block_action = 'r'
        message, _, _ = px_blocker.handle_blocking(ctx, config)
        blocking_message = None
        working_dir = os.path.dirname(os.path.realpath(__file__))
        with open(working_dir + '/px_blocking_messages/ratelimit.txt', 'r') as myfile:
            blocking_message = myfile.read()
        self.assertEqual(message, blocking_message)

    def test_handle_challenge(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        config = PxConfig({'app_id': 'PXfake_app_id'})
        ctx = PxContext({'PATH_INFO': '/fake_app_id/init.js',
                         'HTTP_X_FORWARDED_FOR': '127.0.0.1',
                         'ip': '127.0.0.1',
                         'HTTP_ACCEPT': 'text/html'},
                        config)
        ctx.vid = vid
        ctx.uuid = px_uuid
        ctx.block_action = 'j'
        ctx.block_action_data = 'Bla'

        message, _, _ = px_blocker.handle_blocking(ctx, config)
        blocking_message = 'Bla'
        self.assertEqual(message, blocking_message)

    def test_prepare_properties(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        config = PxConfig({'app_id': 'PXfake_app_id'})
        ctx = PxContext({'PATH_INFO': '/fake_app_id/xhr',
                         'HTTP_X_FORWARDED_FOR': '127.0.0.1',
                         'ip': '127.0.0.1',
                         'HTTP_ACCEPT': 'text/html'},
                        config)
        ctx.vid = vid
        ctx.uuid = px_uuid
        message = px_blocker.prepare_properties(ctx, config)
        expected_message = {'blockScript': '/fake_app_id/captcha/captcha.js?a=&u=8712cef7-bcfa-4bb6-ae99-868025e1908a&v=bf619be8-94be-458a-b6b1-ee81f154c282&m=0',
                            'vid': 'bf619be8-94be-458a-b6b1-ee81f154c282',
                            'jsRef': '',
                            'hostUrl': '/fake_app_id/xhr',
                            'customLogo': None,
                            'appId': 'PXfake_app_id',
                            'uuid': '8712cef7-bcfa-4bb6-ae99-868025e1908a',
                            'logoVisibility': 'hidden',
                            'jsClientSrc': '/fake_app_id/init.js',
                            'firstPartyEnabled': 'true',
                            'refId': '8712cef7-bcfa-4bb6-ae99-868025e1908a',
                            'cssRef': ''}
        self.assertDictEqual(message, expected_message)
        expected_message['blockScript'] = '/fake_app/captcha/captcha.js?a=&u=8712cef7-bcfa-4bb6-ae99-868025e1908a&v=bf619be8-94be-458a-b6b1-ee81f154c282&m=0'
        self.assertNotEqual(message, expected_message)





