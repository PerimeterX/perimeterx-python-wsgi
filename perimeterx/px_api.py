import sys
import px_httpc
import time
import px_constants
import json



def send_risk_request(ctx, config):
    body = prepare_risk_body(ctx, config)
    default_headers = {
        'Authorization': 'Bearer ' + config.auth_token,
        'Content-Type': 'application/json'
    }
    response = px_httpc.send(full_url=config.server_host + px_constants.API_RISK,body=json.dumps(body),config=config, headers=default_headers,method='POST')
    return json.loads(response.content)

def verify(ctx, config):
    logger = config.logger
    logger.debug("PXVerify")
    try:
        start = time.time()
        response = send_risk_request(ctx, config)
        risk_rtt = time.time() - start
        logger.debug('Risk call took ' + str(risk_rtt) + 'ms')

        if response:
            score = response['score']
            ctx['score'] = score
            ctx['uuid'] = response['uuid']
            ctx['block_action'] = response['action']
            ctx['risk_rtt'] = risk_rtt
            if score >= config.blocking_score:
                if response['action'] == 'j' and response.get('action_data') is not None and response.get('action_data').get('body') is not None:
                    logger.debug("PXVerify received javascript challenge action")
                    ctx['block_action_data'] = response.get('action_data').get('body')
                    ctx['block_reason'] = 'challenge'
                elif response['action'] is 'r':
                    logger.debug("PXVerify received javascript ratelimit action")
                    ctx['block_reason'] = 'exceeded_rate_limit'
                else:
                    logger.debug("PXVerify block score threshold reached, will initiate blocking")
                    ctx['block_reason'] = 's2s_high_score'
            else:
                ctx['pass_reason'] = 's2s'

            logger.debug("PxAPI[verify] S2S completed")
            return True
        else:
            return False
    except:
        logger.error('couldnt complete server to server verification')
        return False


def prepare_risk_body(ctx, config):
    logger = config.logger
    logger.debug("PxAPI[send_risk_request]")
    body = {
        'request': {
            'ip': ctx.get('ip'),
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
            'module_version': config.module_version,
            'risk_mode': config.module_mode,
            'px_cookie_hmac': ctx.get('cookie_hmac', ''),
            'request_cookie_names': ctx.get('cookie_names', '')
        }
    }

    body = add_original_token_data(ctx, body)

    if ctx['s2s_call_reason'] == 'cookie_decryption_failed':
        logger.debug('attaching orig_cookie to request')
        body['additional']['px_cookie_orig'] = ctx.get('px_orig_cookie')

    if ctx['s2s_call_reason'] in ['cookie_expired', 'cookie_validation_failed']:
        logger.debug('attaching px_cookie to request')
        body['additional']['px_cookie'] = ctx.get('decoded_cookie')

    logger.debug("PxAPI[send_risk_request] request body: " + str(body))
    return body

def add_original_token_data(ctx, body):
    if ctx.get('original_uuid'):
        body['additional']['original_uuid'] = ctx.get('original_uuid')
    if ctx.get('original_token_error'):
        body['additional']['original_token_error'] = ctx.get('original_token_error')
    if ctx.get('original_token'):
        body['additional']['original_token'] = ctx.get('original_token')
    if ctx.get('decoded_original_token'):
        body['additional']['decoded_original_token'] = ctx.get('decoded_original_token')
    return body

def format_headers(headers):
    ret_val = []
    for key in headers.keys():
        ret_val.append({'name': key, 'value': headers[key]})
    return ret_val
