import px_httpc


def verify(ctx, config):
    captcha = ctx.get('px_captcha')
    if not captcha:
        return False

    split_captcha = captcha.split(':')
    captcha_value = split_captcha[0]
    vid = split_captcha[1]
    uuid = split_captcha[2]

    if not vid or not captcha_value:
        return False

    response = send_captcha_request(vid, uuid, captcha_value, ctx, config)
    return response and response.get('status', 1) == 0


def send_captcha_request(vid, uuid, captcha_value, ctx, config):
    body = {
        'request': {
            'ip': ctx.get('socket_ip'),
            'headers': format_headers(ctx.get('headers')),
            'uri': ctx.get('uri')
        },
        'pxCaptcha': captcha_value,
        'vid': vid,
        'uuid': uuid,
        'hostname': ctx.get('hostname')
    }
    response = px_httpc.send('/api/v1/risk/captcha', body=body, config=config)

    return response


def format_headers(headers):
    ret_val = []
    for key in headers.keys():
        ret_val.append({'name': key, 'value': headers[key]})
    return ret_val

