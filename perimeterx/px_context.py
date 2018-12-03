import Cookie
from px_constants import *


class PxContext(object):

    def __init__(self, environ, config):

        logger = config.logger
        headers = {}

        # Default values
        http_method = ''
        http_version = ''
        http_protocol = ''
        px_cookies = {}
        request_cookie_names = []
        cookie_origin = "cookie"
        vid = ''

        # Extracting: Headers, user agent, http method, http version
        for key in environ.keys():
            if key.startswith('HTTP_') and environ.get(key):
                header_name = key.split('HTTP_')[1].replace('_', '-').lower()
                if header_name not in config.sensitive_headers:
                    headers[header_name] = environ.get(key)
            if key == 'REQUEST_METHOD':
                http_method = environ.get(key)
            if key == 'SERVER_PROTOCOL':
                protocol_split = environ.get(key, '').split('/')
                if protocol_split[0].startswith('HTTP'):
                    http_protocol = protocol_split[0].lower() + '://'
                if len(protocol_split) > 1:
                    http_version = protocol_split[1]
            if key == 'CONTENT_TYPE' or key == 'CONTENT_LENGTH':
                headers[key.replace('_', '-').lower()] = environ.get(key)
            if key == 'HTTP_' + MOBILE_SDK_HEADER.replace('-', '_').upper():
                headers[MOBILE_SDK_HEADER] = environ.get(key, '')

        original_token = ''
        mobile_header = headers.get(MOBILE_SDK_HEADER)
        if mobile_header is None:
            cookies = Cookie.SimpleCookie(environ.get('HTTP_COOKIE', ''))
            cookie_keys = cookies.keys()

            for key in cookie_keys:
                request_cookie_names.append(key)
                if key == PREFIX_PX_COOKIE_V1 or key == PREFIX_PX_COOKIE_V3:
                    logger.debug('Found cookie prefix:' + key)
                    px_cookies[key] = cookies.get(key).value
            if '_pxvid' in cookie_keys:
                vid = cookies.get('_pxvid').value
        else:
            cookie_origin = "header"
            original_token = headers.get(MOBILE_SDK_ORIGINAL_HEADER)
            logger.debug('Mobile SDK token detected')
            cookie_name, cookie = self.get_token_object(config, mobile_header)
            px_cookies[cookie_name] = cookie

        user_agent = headers.get('user-agent', '')
        uri = environ.get('PATH_INFO') or ''
        full_url = http_protocol + (headers.get('host') or environ.get('SERVER_NAME') or '') + uri
        hostname = headers.get('host')
        sensitive_route = len(
            filter(lambda sensitive_route_item: uri.startswith(sensitive_route_item), config.sensitive_routes)) > 0
        whitelist_route = len(
            filter(lambda whitelist_route_item: uri.startswith(whitelist_route_item), config.whitelist_routes)) > 0
        query_params = environ.get('QUERY_STRING') if environ.get('QUERY_STRING') else ''
        self._headers = headers
        self._http_method = http_method
        self._http_version = http_version
        self._user_agent = user_agent
        self._full_url = full_url
        self._uri = uri
        self._hostname = hostname
        self._px_cookies = px_cookies
        self._cookie_names = request_cookie_names
        self._risk_rtt = 0
        self._ip = self.extract_ip(config, environ)
        self._vid = vid
        self._uuid = ''
        self._query_params = query_params
        self._sensitive_route = sensitive_route
        self._whitelist_route = whitelist_route
        self._s2s_call_reason = 'none'
        self._cookie_origin = cookie_origin
        self._is_mobile = cookie_origin == "header"
        self._score = -1
        self._block_reason = ''
        self._decoded_cookie = ''
        self._block_action = ''
        self._block_action_data = ''
        self._pass_reason = ''
        self._cookie_hmac = ''
        self._px_orig_cookie = ''
        self._original_token_error = ''
        self._original_uuid = ''
        self._decoded_original_token = ''
        self._original_token = original_token


    def get_token_object(self, config, token):
        result = {}
        logger = config.logger
        sliced_token = token.split(":", 1)
        if len(sliced_token) > 1:
            key = sliced_token.pop(0)
            if key == PREFIX_PX_TOKEN_V1 or key == PREFIX_PX_TOKEN_V3:
                logger.debug('Found token prefix:' + key)
                return key, sliced_token[0]
        return PREFIX_PX_TOKEN_V3, token

    def extract_ip(self, config, environ):
        ip = environ.get('HTTP_X_FORWARDED_FOR') if environ.get('HTTP_X_FORWARDED_FOR') else environ.get('REMOTE_ADDR')
        ip_headers = config.ip_headers
        logger = config.logger
        if ip_headers:
            try:
                for ip_header in ip_headers:
                    ip_header_name = 'HTTP_' + ip_header.replace('-', '_').upper()
                    if environ.get(ip_header_name):
                        return environ.get(ip_header_name)
            except:
                logger.debug('Failed to use IP_HEADERS from config')
        if config.get_user_ip:
            ip = config.get_user_ip(environ)
        return ip

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers):
        self._headers = headers

    @property
    def http_method(self):
        return self._http_method

    @http_method.setter
    def http_method(self, http_method):
        self._http_method = http_method

    @property
    def http_version(self):
        return self._http_version

    @http_version.setter
    def http_version(self, http_version):
        self._http_version = http_version

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, user_agent):
        self._user_agent = user_agent

    @property
    def full_url(self):
        return self._full_url

    @full_url.setter
    def full_url(self, full_url):
        self._full_url = full_url

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, uri):
        self._uri = uri

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, hostname):
        self._hostname = hostname

    @property
    def px_cookies(self):
        return self._px_cookies

    @px_cookies.setter
    def px_cookies(self, px_cookies):
        self._px_cookies = px_cookies

    @property
    def cookie_names(self):
        return self._cookie_names

    @cookie_names.setter
    def cookie_names(self, cookie_names):
        self._cookie_names = cookie_names

    @property
    def risk_rtt(self):
        return self._risk_rtt

    @risk_rtt.setter
    def risk_rtt(self, risk_rtt):
        self._risk_rtt = risk_rtt

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, ip):
        self._ip = ip

    @property
    def vid(self):
        return self._vid

    @vid.setter
    def vid(self, vid):
        self._vid = vid

    @property
    def query_params(self):
        return self._query_params

    @query_params.setter
    def query_params(self, query_params):
        self._query_params = query_params

    @property
    def sensitive_route(self):
        return self._sensitive_route

    @sensitive_route.setter
    def sensitive_route(self, sensitive_route):
        self._sensitive_route = sensitive_route

    @property
    def whitelist_route(self):
        return self._whitelist_route

    @whitelist_route.setter
    def whitelist_route(self, whitelist_route):
        self._whitelist_route = whitelist_route

    @property
    def s2s_call_reason(self):
        return self._s2s_call_reason

    @s2s_call_reason.setter
    def s2s_call_reason(self, s2s_call_reason):
        self._s2s_call_reason = s2s_call_reason

    @property
    def cookie_origin(self):
        return self._cookie_origin

    @cookie_origin.setter
    def cookie_origin(self, cookie_origin):
        self._cookie_origin = cookie_origin

    @property
    def original_token(self):
        return self._original_token

    @original_token.setter
    def original_token(self, original_token):
        self._original_token = original_token

    @property
    def is_mobile(self):
        return self._is_mobile

    @is_mobile.setter
    def is_mobile(self, is_mobile):
        self._is_mobile = is_mobile

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        self._uuid = uuid

    @property
    def block_reason(self):
        return self._block_reason

    @block_reason.setter
    def block_reason(self, block_reason):
        self._block_reason = block_reason

    @property
    def decoded_cookie(self):
        return self._decoded_cookie

    @decoded_cookie.setter
    def decoded_cookie(self, decoded_cookie):
        self._decoded_cookie = decoded_cookie

    @property
    def block_action(self):
        return self._block_action

    @block_action.setter
    def block_action(self, block_action):
        self._block_action = block_action

    @property
    def block_action_data(self):
        return self._block_action_data

    @block_action_data.setter
    def block_action_data(self, block_action_data):
        self._block_action_data = block_action_data

    @property
    def pass_reason(self):
        return self._pass_reason

    @pass_reason.setter
    def pass_reason(self, pass_reason):
        self._pass_reason = pass_reason

    @property
    def cookie_hmac(self):
        return self._cookie_hmac

    @cookie_hmac.setter
    def cookie_hmac(self, cookie_hmac):
        self._cookie_hmac = cookie_hmac

    @property
    def px_orig_cookie(self):
        return self._px_orig_cookie

    @px_orig_cookie.setter
    def px_orig_cookie(self, px_orig_cookie):
        self._px_orig_cookie = px_orig_cookie

    @property
    def original_token_error(self):
        return self._original_token_error

    @original_token_error.setter
    def original_token_error(self, original_token_error):
        self._original_token_error = original_token_error

    @property
    def original_uuid(self):
        return self._original_uuid

    @original_uuid.setter
    def original_uuid(self, original_uuid):
        self._original_uuid = original_uuid

    @property
    def decoded_original_token(self):
        return self._decoded_original_token

    @decoded_original_token.setter
    def decoded_original_token(self, decoded_original_token):
        self._decoded_original_token = decoded_original_token
