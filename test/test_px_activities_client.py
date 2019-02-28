from perimeterx import px_activities_client
from perimeterx.px_context import PxContext
from perimeterx.px_config import PxConfig
from perimeterx import px_constants
import unittest
import mock
from unittest import TestCase
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request


class TestWorkMockingModule(TestCase):


    @classmethod
    def setUpClass(cls):
        cls.config = PxConfig({'app_id': 'PXfake_app_id'})
        cls.headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'content_length': '100'}

    def test_send_to_perimterx(self):
        with mock.patch('perimeterx.px_activities_client.ACTIVITIES_BUFFER') as mock_buffer:
            builder = EnvironBuilder(headers=self.headers)

            env = builder.get_environ()
            request = Request(env)
            context = PxContext(request, self.config)

            context.score = 100
            context.uuid = 'uuid'
            context.vid = 'vid'
            context.http_method = 'post'
            context.http_version = '1.1'
            context.decoded_cookie = '{"u":"83c756b0-fbbd-11e8-956e-0d1c8297fb79", "v":"75e52040-f6f9-11e8-bc4c-994724030299","t":1544368677086,"s":0,"a":"c"}'
            context.risk_rtt = '2342'
            context.cookie_origin = 'header'
            context.block_action = 'c'
            details = {
                'block_score': context.score,
                'client_uuid': context.uuid,
                'block_reason': context.block_reason,
                'http_method': context.http_method,
                'http_version': context.http_version,
                'px_cookie': context.decoded_cookie,
                'risk_rtt': context.risk_rtt,
                'cookie_origin': context.cookie_origin,
                'block_action': context.block_action,
                'module_version': px_constants.MODULE_VERSION,
                'simulated_block': self.config.module_mode is px_constants.MODULE_MODE_MONITORING,
            }
            px_activities_client.send_to_perimeterx(activity_type='page_requested', ctx=context, config=self.config,
                                                    detail=details)
            mock_buffer.append.assert_called_once()
            args = mock_buffer.method_calls.pop(0)[1][0]
            self.assertEqual(args['px_app_id'], 'PXfake_app_id')
            self.assertEqual(args['vid'], 'vid')
            self.assertEqual(args['uuid'], 'uuid')


    def test_send_block_activity(self):
        with mock.patch('perimeterx.px_activities_client.send_to_perimeterx') as mock_send_to_perimeterx:
            builder = EnvironBuilder(headers=self.headers)

            env = builder.get_environ()
            request = Request(env)
            context = PxContext(request, self.config)

            context.score = 100
            context.uuid = 'uuid'
            context.vid = 'vid'
            context.http_method = 'post'
            context.http_version = '1.1'
            context.decoded_cookie = '{"u":"83c756b0-fbbd-11e8-956e-0d1c8297fb79", "v":"75e52040-f6f9-11e8-bc4c-994724030299","t":1544368677086,"s":0,"a":"c"}'
            context.risk_rtt = '2342'
            context.cookie_origin = 'header'
            context.block_action = 'c'

            px_activities_client.send_block_activity(ctx=context, config=self.config)
            mock_send_to_perimeterx.assert_called_once()
            args = mock_send_to_perimeterx.call_args[0]
            expected = {
                'block_action': 'c',
                'block_reason': '',
                'block_score': 100,
                'block_uuid': 'uuid',
                'cookie_origin': 'header',
            }
            self.assertEqual(args[0], 'block')
            details = args[3]
            self.assertEqual(details['block_action'], expected['block_action'])
            self.assertEqual(details['block_uuid'], 'uuid')
            self.assertEqual(details['cookie_origin'], 'header')


    # def test_send_page_requested_activity(self):
    #     with mock.patch('perimeterx.px_activities_client.send_to_perimeterx') as mock_send_to_perimeterx:
    #         builder = EnvironBuilder(headers=self.headers)
    #
    #         env = builder.get_environ()
    #         request = Request(env)
    #         context = PxContext(request, self.config)
    #
    #         context.score = 100
    #         context.uuid = 'uuid'
    #         context.vid = 'vid'
    #         context.http_method = 'post'
    #         context.http_version = '1.1'
    #         context.decoded_cookie = '{"u":"83c756b0-fbbd-11e8-956e-0d1c8297fb79", "v":"75e52040-f6f9-11e8-bc4c-994724030299","t":1544368677086,"s":0,"a":"c"}'
    #         context.risk_rtt = '2342'
    #         context.cookie_origin = 'header'
    #         context.block_action = 'c'
    #
    #         px_activities_client.send_page_requested_activity(ctx=context, config=self.config)
    #         mock_send_to_perimeterx.assert_called_once()
    #         args = mock_send_to_perimeterx.call_args[0]
    #         details = {
    #             'client_uuid': 'uuid',
    #             'pass_reason': ctx.pass_reason,
    #             'risk_rtt': ctx.risk_rtt
    #         }
    #         self.assertEqual(args[0], 'block')
    #         details = args[3]
    #         self.assertEqual(details['block_action'], expected['block_action'])
    #         self.assertEqual(details['block_uuid'], 'uuid')
    #         self.assertEqual(details['cookie_origin'], 'header')
