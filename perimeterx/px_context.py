import Cookie


def build_context(environ, config):
    headers = {}

    # Default values
    http_method = 'GET'
    http_version = '1.1'
    http_protocol = 'http://'
    px_cookie = ''
    px_captcha = ''

    # IP Extraction
    if config.get('ip_handler'):
        socket_ip = config.get('ip_handler')(environ)
    else:
        socket_ip = environ.get('REMOTE_ADDR')

    # Extracting: Headers, user agent, http method, http version
    for key in environ.keys():
        if key.startswith('HTTP_') and environ.get(key):
            header_name = key.split('HTTP_')[1].replace('_', '-').lower()
            if header_name not in config.get('sensitive_headers'):
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
    if cookies.get('_px') and cookies.get('_px').value:
        px_cookie = cookies.get('_px').value

    if cookies.get('_pxCaptcha') and cookies.get('_pxCaptcha').value:
        px_captcha = cookies.get('_pxCaptcha').value

    user_agent = headers.get('user-agent')
    uri = environ.get('PATH_INFO') or ''
    full_url = http_protocol + headers.get('host') or environ.get('SERVER_NAME') or '' + uri
    hostname = headers.get('host')
    ctx = {
        'headers': headers,
        'http_method': http_method,
        'http_version': http_version,
        'user_agent': user_agent,
        'socket_ip': socket_ip,
        'full_url': full_url,
        'uri': uri,
        'px_cookie': px_cookie,
        'px_captcha': px_captcha,
        'hostname': hostname
    }
    return ctx
