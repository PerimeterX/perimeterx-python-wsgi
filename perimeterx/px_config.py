import px_constants
from px_logger import Logger


class PxConfig(object):
    def __init__(self, config_dict):
        app_id = config_dict.get('app_id')
        debug_mode = config_dict.get('debug_mode', False)
        module_mode = config_dict.get('module_mode', px_constants.MODULE_MODE_MONITORING)
        custom_logo = config_dict.get('custom_logo', None)
        self._px_app_id = app_id
        self._blocking_score = config_dict.get('blocking_score', 100)
        self._debug_mode = debug_mode
        self._module_version = config_dict.get('module_version', px_constants.MODULE_VERSION)
        self._module_mode = module_mode
        self._server_host = 'sapi.perimeterx.net' if app_id is None else px_constants.SERVER_URL.format(app_id.lower())
        self._collector_host = 'collector.perimeterx.net' if app_id is None else px_constants.COLLECTOR_URL.format(
            app_id.lower())
        self._encryption_enabled = config_dict.get('encryption_enabled', True)
        self._sensitive_headers = config_dict.get('sensitive_headers', ['cookie', 'cookies'])
        self._send_page_activities = config_dict.get('send_page_activities', True)
        self._api_timeout_ms = config_dict.get('api_timeout', 500)
        self._custom_logo = custom_logo
        self._css_ref = config_dict.get('_custom_logo', '')
        self._js_ref = config_dict.get('js_ref', '')
        self._is_mobile = config_dict.get('is_mobile', False)
        self._monitor_mode = 0 if module_mode is px_constants.MODULE_MODE_MONITORING else 1
        self._module_enabled = config_dict.get('module_enabled', True)
        self._auth_token = config_dict.get('auth_token', None)
        self._is_mobile = config_dict.get('is_mobile', False)
        self._first_party = config_dict.get('first_party', True)
        self._first_party_xhr_enabled = config_dict.get('first_party_xhr_enabled', True)
        self._ip_headers = config_dict.get('ip_headers', [])
        self._proxy_url = config_dict.get('proxy_url', None)
        self._max_buffer_len = config_dict.get('max_buffer_len', 30)
        self._sensitive_routes = config_dict.get('sensitive_routes', [])
        self._whitelist_routes = config_dict.get('whitelist_routes', [])
        self._block_html = 'BLOCK'
        self._logo_visibility = 'visible' if custom_logo is not None else 'hidden'
        self._telemetry_config = self.__create_telemetry_config()

        self._auth_token = config_dict.get('auth_token', None)
        self._cookie_key = config_dict.get('cookie_key', None)
        self.__instantiate_user_defined_handlers(config_dict)
        self._logger = Logger(debug_mode, app_id)

    @property
    def module_mode(self):
        return self._module_mode

    @property
    def app_id(self):
        return self._px_app_id

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
        return self._api_timeout_ms / 1000.000

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

    @property
    def get_user_ip(self):
        return self._get_user_ip

    @property
    def sensitive_routes(self):
        return self._sensitive_routes

    @property
    def whitelist_routes(self):
        return self._whitelist_routes

    @property
    def block_html(self):
        return self._block_html

    @property
    def logo_visibility(self):
        return self._logo_visibility

    @property
    def additional_activity_handler(self):
        return self._additional_activity_handler

    @property
    def debug_mode(self):
        return self._debug_mode

    @property
    def max_buffer_len(self):
        return self._max_buffer_len

    @property
    def telemetry_config(self):
        return self._telemetry_config

    @property
    def enrich_custom_parameters(self):
        return self._enrich_custom_parameters

    def __instantiate_user_defined_handlers(self, config_dict):
        self._custom_request_handler = self.__set_handler('custom_request_handler', config_dict)
        self._get_user_ip = self.__set_handler('get_user_ip', config_dict)
        self._additional_activity_handler = self.__set_handler('additional_activity_handler', config_dict)
        self._enrich_custom_parameters = self.__set_handler('enrich_custom_parameters', config_dict)

    def __set_handler(self, function_name, config_dict):
        return config_dict.get(function_name) if config_dict.get(function_name) and callable(
            config_dict.get(function_name)) else None

    def __create_telemetry_config(self):
        config = self.__dict__
        mutated_config = {}
        for key, value in config.iteritems():
            mutated_config[key[1:].upper()] = value
        return mutated_config
