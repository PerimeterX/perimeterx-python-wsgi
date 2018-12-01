import Cookie
from px_constants import *

def build_context(environ, config):
    logger = config.logger
    headers = {}

    # Default values
    http_method = 'GET'
    http_version = '1.1'
    http_protocol = 'http://'
    px_cookies = {}
    request_cookie_names = list()
    cookie_origin = "cookie"
    original_token = None

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
        if key == 'HTTP_' + MOBILE_SDK_HEADER.replace('-','_').upper():
            headers[MOBILE_SDK_HEADER] = environ.get(key, '')

    mobile_header = headers.get(MOBILE_SDK_HEADER)
    vid = None
    original_token = None
    if mobile_header is None:
        cookies = Cookie.SimpleCookie(environ.get('HTTP_COOKIE', ''))
        cookie_keys = cookies.keys()

        for key in cookie_keys:
            request_cookie_names.append(key)
            if key == PREFIX_PX_COOKIE_V1 or key == PREFIX_PX_COOKIE_V3:
                logger.debug('Found cookie prefix:' + key)
                px_cookies[key] = cookies.get(key).value
        vid = None
        if '_pxvid' in cookie_keys:
            vid = cookies.get('_pxvid').value
        else:
            vid = ''
    else:
        cookie_origin = "header"
        original_token = headers.get(MOBILE_SDK_ORIGINAL_HEADER)
        logger.debug('Mobile SDK token detected')
        cookie_name, cookie = get_token_object(config, mobile_header)
        px_cookies[cookie_name] = cookie

    user_agent = headers.get('user-agent','')
    uri = environ.get('PATH_INFO') or ''
    full_url = http_protocol + (headers.get('host') or environ.get('SERVER_NAME') or '') + uri
    hostname = headers.get('host')
    sensitive_route = len(filter(lambda sensitive_route_item : uri.startswith(sensitive_route_item), config.sensitive_routes)) > 0
    whitelist_route = len(filter(lambda whitelist_route_item : uri.startswith(whitelist_route_item), config.whitelist_routes)) > 0
    ctx = {
        'headers': headers,
        'http_method': http_method,
        'http_version': http_version,
        'user_agent': user_agent,
        'full_url': full_url,
        'uri': uri,
        'hostname': hostname,
        'px_cookies': px_cookies,
        'cookie_names': request_cookie_names,
        'risk_rtt': 0,
        'ip': extract_ip(config, environ),
        'vid': vid if vid else None,
        'query_params': environ['QUERY_STRING'],
        'sensitive_route': sensitive_route,
        'whitelist_route': whitelist_route,
        's2s_call_reason': 'none',
        'cookie_origin':cookie_origin,
        'original_token': original_token,
        'is_mobile': cookie_origin == "header"
    }

    return ctx

def get_token_object(config, token):
    result = {}
    logger = config.logger
    sliced_token = token.split(":", 1)
    if len(sliced_token) > 1:
        key = sliced_token.pop(0)
        if key == PREFIX_PX_TOKEN_V1 or key == PREFIX_PX_TOKEN_V3:
            logger.debug('Found token prefix:' + key)
            return key, sliced_token[0]
    return PREFIX_PX_TOKEN_V3, token

def extract_ip(config, environ):
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
