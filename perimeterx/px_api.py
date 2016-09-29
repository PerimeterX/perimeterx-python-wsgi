import sys
import px_httpc


def send_risk_request(ctx, config):
    body = prepare_risk_body(ctx, config)
    return px_httpc.send('/api/v1/risk', body, config)


def verify(ctx, config):
    logger = config['logger']
    try:
        response = send_risk_request(ctx, config)
        if response:
            ctx['risk_score'] = response['scores']['non_human']
            ctx['uuid'] = response['uuid']
            if ctx['risk_score'] >= config['blocking_score']:
                ctx['block_reason'] = 's2s_high_score'

            return True
        else:
            return False
    except:
        print sys.exc_info()[0]
        logger.error('couldnt complete server to server verification ')
        return False


def prepare_risk_body(ctx, config):
    body = {
        'request': {
            'ip': ctx.get('socket_ip'),
            'headers': format_headers(ctx.get('headers')),
            'uri': ctx.get('uri'),
            'url': ctx.get('full_url', '')
        },
        'vid': ctx.get('vid', ''),
        'uuid': ctx.get('uuid', ''),
        'additional': {
            's2s_call_reason': ctx.get('s2s_call_reason', ''),
            'http_method': ctx.get('http_method', ''),
            'http_version': ctx.get('http_version', ''),
            'module_version': config.get('module_version', ''),
            'risk_mode': config.get('module_mode', '')
        }
    }
    if ctx.get('s2s_call_reason', '') in ['cookie_expired', 'cookie_validation_failed']:
        body['additional']['px_cookie'] = ctx.get('decoded_cookie')

    return body


def format_headers(headers):
    ret_val = []
    for key in headers.keys():
        ret_val.append({'name': key, 'value': headers[key]})
    return ret_val
