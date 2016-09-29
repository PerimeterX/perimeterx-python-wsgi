import px_httpc


def verify(ctx, config):
    captcha = ctx.get('px_captcha')
    if not captcha:
        return False

    split_captcha = captcha.split(':')
    captcha_value = split_captcha[0]
    vid = split_captcha[1]

    if not vid or not captcha_value:
        return False

    response = send_captcha_request(vid, captcha_value, ctx, config)
    return response.get('status', 1) == 0


def send_captcha_request(vid, captcha_value, ctx, config):
    body = {
        'request': {
            'ip': ctx.get('socket_ip'),
            'headers': format_headers(ctx.get('headers')),
            'uri': ctx.get('uri')
        },
        'pxCaptcha': captcha_value,
        'vid': vid,
        'hostname': ctx.get('hostname')
    }
    response = px_httpc.send('/api/v1/risk/captcha', body=body, config=config)

    return response


def format_headers(headers):
    ret_val = []
    for key in headers.keys():
        ret_val.append({'name': key, 'value': headers[key]})
    return ret_val
    # private
    # function
    # sendCaptchaRequest($vid, $captcha)
    # {
    # $requestBody = [
    #     'request' = > [
    #     'ip' = > $this->pxCtx->getIp(),
    #                            'headers' = > $this->formatHeaders(),
    #                                                 'uri' = > $this->pxCtx->getUri()
    # ],
    # 'pxCaptcha' = > $captcha,
    #                  'vid' = > $vid,
    #                             'hostname' = > $this->pxCtx->getHostname()
    # ];
    # $headers = [
    #     'Authorization' = > 'Bearer '. $this->pxConfig['auth_token'],
    #                                           'Content-Type' = > 'application/json'
    # ];
    # $response = $this->httpClient->send('/api/v1/risk/captcha', 'POST', $requestBody, $headers, $this->pxConfig[
    #                                                                                                        'api_timeout'], $this->
    # pxConfig['api_connect_timeout']);
    # return $response;
    # }
