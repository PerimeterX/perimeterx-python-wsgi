import unittest

import mock
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request, Response

import perimeterx.px_constants as px_constants
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext
from perimeterx.px_request_verifier import PxRequestVerifier


class TestPxRequestVerifier(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = PxConfig({'app_id': 'PXfake_app_id',
                               'auth_token': '',
                               'module_mode': px_constants.MODULE_MODE_BLOCKING
                               })
        cls.headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'content_length': '100'}
        cls.request_handler = PxRequestVerifier(cls.config)

    def test_verify_request_fp_client_passed(self):
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        response = Response("client data")
        with mock.patch('perimeterx.px_proxy.PxProxy.handle_reverse_request', return_value=response):
            response = self.request_handler.verify_request(context, request)
            self.assertEqual(response.data, "client data")

    def test_verify_static_url(self):
        builder = EnvironBuilder(headers=self.headers, path='/fake.css')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        response = self.request_handler.verify_request(context, request)
        self.assertEqual(response, True)

    def test_verify_whitelist(self):
        config = PxConfig({'app_id': 'PXfake_app_id', 'whitelist_routes': ['whitelisted']})
        builder = EnvironBuilder(headers=self.headers, path='/whitelisted')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        response = self.request_handler.verify_request(context, request)
        self.assertEqual(response, True)

    def test_handle_verification_pass(self):
        config = PxConfig({'app_id': 'PXfake_app_id', 'whitelist_routes': ['whitelisted']})
        builder = EnvironBuilder(headers=self.headers, path='/whitelisted')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 50
        response = self.request_handler.handle_verification(context, request)
        self.assertEqual(response, True)

    def test_handle_verification_failed(self):
        config = PxConfig({'app_id': 'PXfake_app_id', 'whitelist_routes': ['whitelisted']})
        builder = EnvironBuilder(headers=self.headers, path='/whitelisted')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = self.request_handler.handle_verification(context, request)
        self.assertEqual(response.status, '403 Forbidden')

    def test_handle_monitor(self):
        config = PxConfig({'app_id': 'PXfake_app_id',
                               'auth_token': '',
                               'module_mode': px_constants.MODULE_MODE_MONITORING
                               });
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=self.headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response, True)

    def test_bypass_monitor_header_enabled(self):
        config = PxConfig({'app_id': 'PXfake_app_id',
                               'auth_token': '',
                               'module_mode': px_constants.MODULE_MODE_MONITORING,
                               'bypass_monitor_header': 'x-px-block'
                               });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'x-px-block': '1',
                       'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response.status, '403 Forbidden')

    def test_bypass_monitor_header_disabled(self):
        config = PxConfig({'app_id': 'PXfake_app_id',
                               'auth_token': '',
                               'module_mode': px_constants.MODULE_MODE_MONITORING,
                               'bypass_monitor_header': 'x-px-block'
                               });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'x-px-block': '0',
                       'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response, True)

    def test_bypass_monitor_header_configured_but_missing(self):
        config = PxConfig({'app_id': 'PXfake_app_id',
                               'auth_token': '',
                               'module_mode': px_constants.MODULE_MODE_MONITORING,
                               'bypass_monitor_header': 'x-px-block'
                               });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response, True)

    def test_bypass_monitor_header_on_valid_request(self):
        config = PxConfig({'app_id': 'PXfake_app_id',
                               'auth_token': '',
                               'module_mode': px_constants.MODULE_MODE_MONITORING,
                               'bypass_monitor_header': 'x-px-block'
                               });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'x-px-block': '1',
                       'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 0
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response, True)