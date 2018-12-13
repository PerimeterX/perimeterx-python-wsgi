# from perimeterx import px_activities_client
# from perimeterx.px_context import PxContext
# from perimeterx.px_config import PxConfig
# from perimeterx import px_constants
# import MagicMock
# import mock
# import unittest
#
#
# class TestPxActivitiesClient(unittest.TestCase):
#
#     @mock.patch('perimeterx.px_activities_client.send_to_perimeterx')
#     def test_send_to_perimeterx(self, mocked_event):
#         config = PxConfig({'app_id': 'fake_app_id'})
#         context = PxContext({}, config)
#         context.score = 100
#         context.uuid = 'uuid'
#         context.http_method = 's2s high score'
#         context.http_version = '1.1'
#         context.decoded_cookie = '{"u":"83c756b0-fbbd-11e8-956e-0d1c8297fb79","v":"75e52040-f6f9-11e8-bc4c-994724030299","t":1544368677086,"s":0,"a":"c"}'
#         context.risk_rtt = '2342'
#         context.cookie_origin = 'header'
#         context.block_action = 'c'
#         details = {
#             'block_score': context.score,
#             'client_uuid': context.uuid,
#             'block_reason': context.block_reason,
#             'http_method': context.http_method,
#             'http_version': context.http_version,
#             'px_cookie': context.decoded_cookie,
#             'risk_rtt': context.risk_rtt,
#             'cookie_origin': context.cookie_origin,
#             'block_action': context.block_action,
#             'module_version': px_constants.MODULE_VERSION,
#             'simulated_block': config.module_mode is px_constants.MODULE_MODE_MONITORING,
#         }
#         px_activities_client.send_to_perimeterx(activity_type='page_requested', ctx=context, config=config, detail=details)
#         print mock.call_args