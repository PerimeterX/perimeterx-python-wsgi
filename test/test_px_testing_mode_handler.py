import unittest

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from perimeterx import px_testing_mode_handler
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext


class TestTestingModeHandler(unittest.TestCase):


    def test_testing_mode_handling(self):
        config = PxConfig({
            'app_id': 'fake_app_id'
        })
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100',
                   'cookie': '_px3=bd078865fa9627f626d6f7d6828ab595028d2c0974065ab6f6c5a9f80c4593cd:OCIluokZHHvqrWyu8zrWSH8Vu7AefCjrd4CMx/NXsX58LzeV40EZIlPG4gsNMoAYzH88s/GoZwv+DpQa76C21A==:1000:zwT+Rht/YGDNWKkzHtJAB7IiI00u4fOePL/3xWMs1nZ93lzW1XvAMGR2hLlHBmOv8O0CpylEQOZZTK1uQMls6O28Y8aQnTo5DETLkrbhpwCVeNjOcf8GVKTckITwuHfXbEcfHbdtb68s1+jHv1+vt/w/6HZqTzanaIsvFVp8vmA='}
        builder = EnvironBuilder(headers=headers)

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        data, headers, status = px_testing_mode_handler.testing_mode_handling(context, config, {})
        response_json = '{"vid": "", "ip": "127.0.0.1", "decoded_px_cookie": "", "is_made_s2s_api_call": false, "http_method": "GET", "px_cookie_hmac": "", "uuid": "", "http_version": "1.1", "hostname": "localhost", "risk_rtt": 0, "score": -1, "pxde": {}, "module_mode": 0, "pxde_verified": false, "cookie_origin": "cookie", "s2s_call_reason": "none", "sensitive_route": false, "px_cookies": {"_px3": "bd078865fa9627f626d6f7d6828ab595028d2c0974065ab6f6c5a9f80c4593cd:OCIluokZHHvqrWyu8zrWSH8Vu7AefCjrd4CMx/NXsX58LzeV40EZIlPG4gsNMoAYzH88s/GoZwv+DpQa76C21A==:1000:zwT+Rht/YGDNWKkzHtJAB7IiI00u4fOePL/3xWMs1nZ93lzW1XvAMGR2hLlHBmOv8O0CpylEQOZZTK1uQMls6O28Y8aQnTo5DETLkrbhpwCVeNjOcf8GVKTckITwuHfXbEcfHbdtb68s1+jHv1+vt/w/6HZqTzanaIsvFVp8vmA="}, "uri": "/", "full_url": "http://localhost/", "headers": {"Remote-Addr": "127.0.0.1", "Host": "localhost", "X-Forwarded-For": "127.0.0.1", "Content-Length": "0"}, "block_action": "", "user_agent": "", "block_reason": ""}'
        self.assertEqual(data, response_json)

