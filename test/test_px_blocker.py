import os
import unittest

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from perimeterx.px_blocker import PXBlocker
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext


class Test_PXBlocker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = PxConfig({'app_id': 'PXfake_app_id'})
        cls.headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'content-length': '100'}

    def test_is_json_response(self):
        px_blocker = PXBlocker()
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        self.assertFalse(px_blocker.is_json_response(context))
        context.headers['Accept'] = 'application/json'
        self.assertTrue(px_blocker.is_json_response(context))

    def test_handle_blocking(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'

        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        context.vid = vid
        context.uuid = px_uuid
        px_config = PxConfig({'app_id': 'PXfake_app_ip'})
        message, _, _ = px_blocker.handle_blocking(context, px_config)
        working_dir = os.path.dirname(os.path.realpath(__file__))
        with open(working_dir + '/px_blocking_messages/blocking.txt', 'r') as myfile:
            blocking_message = myfile.read()

        self.assertEqual(message, blocking_message)

    def test_handle_ratelimit(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        config = PxConfig({'app_id': 'PXfake_app_id'})
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        context.vid = vid
        context.uuid = px_uuid
        context.block_action = 'r'
        message, _, _ = px_blocker.handle_blocking(context, config)
        blocking_message = None
        working_dir = os.path.dirname(os.path.realpath(__file__))
        with open(working_dir + '/px_blocking_messages/ratelimit.txt', 'r') as myfile:
            blocking_message = myfile.read()
        self.assertEqual(message, blocking_message)

    def test_handle_challenge(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        context.vid = vid
        context.uuid = px_uuid
        context.block_action = 'j'
        context.block_action_data = 'Bla'

        message, _, _ = px_blocker.handle_blocking(context, self.config)
        blocking_message = 'Bla'
        self.assertEqual(message, blocking_message)

    def test_prepare_properties(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        context.vid = vid
        context.uuid = px_uuid
        message = px_blocker.prepare_properties(context, self.config)
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





