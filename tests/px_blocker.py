from perimeterx.px_blocker import PXBlocker


import unittest
from perimeterx.px_config import PXConfig


class Test_PXBlocker(unittest.TestCase):

    def test_is_json_response(self):
        px_blocker = PXBlocker()
        ctx = {
            'headers': {'Accept': 'text/html'}
        }
        self.assertFalse(px_blocker.is_json_response(ctx))
        ctx['headers']['Accept'] = 'application/json'
        self.assertTrue(px_blocker.is_json_response(ctx))

    def test_handle_blocking(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        ctx = {
            'headers': {'Accept': 'text/html'},
            'vid': vid,
            'uuid': px_uuid
        }
        px_config = PXConfig({'app_id': 'PXfake_app_ip'})
        message, _, _ = px_blocker.handle_blocking(ctx, px_config)
        blocking_message = None
        with open('./px_blocking_messages/blocking.txt', 'r') as myfile:
            blocking_message = myfile.read()
        self.assertEqual(message, blocking_message)

    def test_handle_ratelimit(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        ctx = {
            'headers': {'Accept': 'text/html'},
            'vid': vid,
            'uuid': px_uuid,
            'block_action': 'r'
        }
        px_config = PXConfig({'app_id': 'PXfake_app_ip'})
        message, _, _ = px_blocker.handle_blocking(ctx, px_config)
        blocking_message = None
        with open('./px_blocking_messages/ratelimit.txt', 'r') as myfile:
            blocking_message = myfile.read()
        self.assertEqual(message, blocking_message)

    def test_handle_challenge(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        ctx = {
            'headers': {'Accept': 'text/html'},
            'vid': vid,
            'uuid': px_uuid,
            'block_action': 'j',
            'block_action_data': 'Bla'
        }
        px_config = PXConfig({'app_id': 'PXfake_app_ip'})
        message, _, _ = px_blocker.handle_blocking(ctx, px_config)
        blocking_message = 'Bla'
        self.assertEqual(message, blocking_message)

    def test_prepare_properties(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        ctx = {
            'headers': {'Accept': 'text/html'},
            'vid': vid,
            'uuid': px_uuid,
        }
        px_config = PXConfig({'app_id': 'PXfake_app_ip'})
        message = px_blocker.prepare_properties(ctx, px_config)
        expected_message = {'blockScript': '/fake_app_ip/captcha/captcha.js?a=None&u=8712cef7-bcfa-4bb6-ae99-868025e1908a&v=bf619be8-94be-458a-b6b1-ee81f154c282&m=0',
                            'vid': 'bf619be8-94be-458a-b6b1-ee81f154c282',
                            'jsRef': '',
                            'hostUrl': '/fake_app_ip/xhr',
                            'customLogo': None,
                            'appId': 'pxfake_app_ip',
                            'uuid': '8712cef7-bcfa-4bb6-ae99-868025e1908a',
                            'logoVisibility': 'hidden',
                            'jsClientSrc': '/fake_app_ip/init.js',
                            'firstPartyEnabled': True,
                            'refId': '8712cef7-bcfa-4bb6-ae99-868025e1908a',
                            'cssRef': ''}
        self.assertDictEqual(message, expected_message)
        expected_message['blockScript'] = '/fake_app/captcha/captcha.js?a=None&u=8712cef7-bcfa-4bb6-ae99-868025e1908a&v=bf619be8-94be-458a-b6b1-ee81f154c282&m=0'
        self.assertNotEqual(message, expected_message)





