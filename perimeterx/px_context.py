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

    user_agent = headers.get('user-agent')
    uri = environ.get('PATH_INFO') or ''
    full_url = http_protocol + headers.get('host') or environ.get('SERVER_NAME') or '' + uri
    hostname = headers.get('host')
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
        'vid': vid,
        'query_params': environ['QUERY_STRING']
    }
    return ctx

def extract_ip(config, environ):
    ip_default = environ.get('HTTP_X_FORWARDED_FOR')
    ip_headers = config.ip_headers
    logger = config.logger
    if not ip_headers:
        try:
            for ip_header in ip_headers:
                ip_header_name = 'HTTP_' + ip_header.upper()
                if environ.get(ip_header_name):
                    return environ.get(ip_header_name)
        except:
            logger.debug('Failed to use IP_HEADERS from config')
    return ip_default



