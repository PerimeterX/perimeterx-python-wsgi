import px_httpc
import time
import px_constants
import json
import re

custom_params = {
    'custom_param1': '',
    'custom_param2': '',
    'custom_param3': '',
    'custom_param4': '',
    'custom_param5': '',
    'custom_param6': '',
    'custom_param7': '',
    'custom_param8': '',
    'custom_param9': '',
    'custom_param10': ''
}


def send_risk_request(ctx, config):
    body = prepare_risk_body(ctx, config)
    default_headers = {
        'Authorization': 'Bearer ' + config.auth_token,
        'Content-Type': 'application/json'
    }
    response = px_httpc.send(full_url=config.server_host + px_constants.API_RISK, body=json.dumps(body), config=config,
                             headers=default_headers, method='POST')
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
            ctx.score = response.get('score')
            ctx.uuid = response.get('uuid')
            ctx.block_action = response.get('action')
            ctx.risk_rtt = risk_rtt
            if ctx.score >= config.blocking_score:
                if response.get('action') == px_constants.ACTION_CHALLENGE and response.get('action_data') is not None and response.get(
                        'action_data').get('body') is not None:
                    logger.debug("PXVerify received javascript challenge action")
                    ctx.block_action_data = response.get('action_data').get('body')
                    ctx.block_reason = 'challenge'
                elif response.get('action') is px_constants.ACTION_RATELIMIT:
                    logger.debug("PXVerify received javascript ratelimit action")
                    ctx.block_reason = 'exceeded_rate_limit'
                else:
                    logger.debug("PXVerify block score threshold reached, will initiate blocking")
                    ctx.block_reason = 's2s_high_score'
            else:
                ctx.pass_reason = 's2s'

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
            'ip': ctx.ip,
            'headers': format_headers(ctx.headers),
            'uri': ctx.uri,
            'url': ctx.full_url,
            'firstParty': 'true' if config.first_party else 'false'
        },
        'additional': {
            's2s_call_reason': ctx.s2s_call_reason,
            'http_method': ctx.http_method,
            'http_version': ctx.http_version,
            'module_version': config.module_version,
            'risk_mode': config.module_mode,
            'cookie_origin': ctx.cookie_origin
        }
    }
    if ctx.vid:
        body['vid'] = ctx.vid
    if ctx.uuid:
        body['uuid'] = ctx.uuid
    if ctx.cookie_hmac:
        body['additional']['px_cookie_hmac'] = ctx.cookie_hmac
    if ctx.cookie_names:
        body['additional']['request_cookie_names'] = ctx.cookie_names


    body = add_original_token_data(ctx, body)

    if config.enrich_custom_parameters:
        risk_custom_params = config.enrich_custom_parameters(custom_params)
        for param in risk_custom_params:
            if re.match('^custom_param\d$', param) and risk_custom_params[param]:
                body['additional'][param] = risk_custom_params[param]

    if ctx.s2s_call_reason == 'cookie_decryption_failed':
        logger.debug('attaching orig_cookie to request')
        body['additional']['px_orig_cookie'] = ctx.px_orig_cookie

    if ctx.s2s_call_reason in ['cookie_expired', 'cookie_validation_failed']:
        logger.debug('attaching px_cookie to request')
        body['additional']['px_cookie'] = ctx.decoded_cookie

    logger.debug("PxAPI[send_risk_request] request body: " + str(body))
    return body


def add_original_token_data(ctx, body):
    if ctx.original_uuid:
        body['additional']['original_uuid'] = ctx.original_uuid
    if ctx.original_token_error:
        body['additional']['original_token_error'] = ctx.original_token_error
    if ctx.original_token:
        body['additional']['original_token'] = ctx.original_token
    if ctx.decoded_original_token:
        body['additional']['decoded_original_token'] = ctx.decoded_original_token
    return body


def format_headers(headers):
    ret_val = []
    for key in headers.keys():
        ret_val.append({'name': key, 'value': headers[key]})
    return ret_val
