from perimeterx.px_config import PxConfig
import unittest
from perimeterx import px_constants
class TestPXConfig(unittest.TestCase):

    def test_constructor(self):
        config_dict = {'app_id': 'PXfake_app_id', 'debug_mode': True, 'module_mode': px_constants.MODULE_MODE_BLOCKING}
        config = PxConfig(config_dict)
        self.assertEqual(config._monitor_mode, 1)
        self.assertEqual(config.debug_mode, True)
        self.assertEqual(config.server_host, 'sapi-pxfake_app_id.perimeterx.net')
        self.assertEqual(config.collector_host, 'collector-pxfake_app_id.perimeterx.net')