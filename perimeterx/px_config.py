import px_constants
from px_logger import Logger

class PXConfig(object):
    def __init__(self, config_dict):
        app_id = config_dict.get('app_id')
        debug_mode = config_dict.get('debug_mode', False)
        module_mode = config_dict.get('module_mode', px_constants.MODULE_MODE_MONITORING)
        self._app_id = app_id
        self._blocking_score = config_dict.get('blocking_score', 100)
        self._debug_mode = debug_mode
        self._module_version = config_dict.get('module_version', px_constants.MODULE_VERSION)
        self._module_mode = module_mode
        self._server_host = 'sapi.perimeterx.net' if app_id is None else px_constants.SERVER_URL.format(app_id.lower())
        self._collector_host = 'collector.perimeterx.net' if app_id is None else px_constants.COLLECTOR_URL.format(app_id.lower())
        self._encryption_enabled = config_dict.get('encryption_enabled', True)
        self._sensitive_headers = config_dict.get('sensitive_headers', ['cookie', 'cookies'])
        self._send_page_activities = config_dict.get('send_page_activities', True)
        self._api_timeout = config_dict.get('api_timeout', 500)
        self._custom_logo = config_dict.get('custom_logo', '')
        self._css_ref = config_dict.get('_custom_logo', '')
        self._js_ref = config_dict.get('js_ref', '')
        self._is_mobile = config_dict.get('is_mobile', False)
        self._monitor_mode = 0 if module_mode is px_constants.MODULE_MODE_MONITORING else 1
        self._module_enabled = config_dict.get('module_enabled', True)
        self._cookie_key = config_dict.get('cookie_key', None)
        self._auth_token = config_dict.get('auth_token', None)
        self._is_mobile = config_dict.get('is_mobile', False)
        self._first_party = config_dict.get('first_party', True)
        self._first_party_xhr_enabled = config_dict.get('first_party_xhr_enabled', True)
        self._logger = Logger(debug_mode)
        self._ip_headers = config_dict.get('ip_headers', [])
        self._proxy_url = config_dict.get('proxy_url', None)
        self._custom_request_handler = config_dict.get('custom_request_handler', None)
        self._custom_block_handler = config_dict.get('custom_block_handler', None)

    @property
    def module_mode(self):
        return self._module_mode

    @property
    def app_id(self):
        return self._app_id

    @property
    def logger(self):
        return self._logger

    @property
    def auth_token(self):
        return self._auth_token

    @property
    def cookie_key(self):
        return self._cookie_key

    @property
    def server_host(self):
        return self._server_host

    @property
    def api_timeout(self):
        return self._api_timeout

    @property
    def module_enabled(self):
        return self._module_enabled

    @property
    def ip_headers(self):
        return self._ip_headers

    @property
    def sensitive_headers(self):
        return self._sensitive_headers

    @property
    def proxy_url(self):
        return self._proxy_url

    @property
    def custom_request_handler(self):
        return self._custom_request_handler

    @property
    def custom_block_handler(self):
        return self._custom_block_handler

    @property
    def blocking_score(self):
        return self._blocking_score

    @property
    def encryption_enabled(self):
        return self._encryption_enabled

    @property
    def module_version(self):
        return self._module_version

    @property
    def send_page_activities(self):
        return self._send_page_activities

    @property
    def custom_logo(self):
        return self._custom_logo

    @property
    def css_ref(self):
        return self._css_ref

    @property
    def js_ref(self):
        return self._js_ref

    @property
    def first_party(self):
        return self._first_party

    @property
    def first_party_xhr_enabled(self):
        return self._first_party_xhr_enabled

    @property
    def collector_host(self):
        return self._collector_host
