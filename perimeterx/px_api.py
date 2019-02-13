import json
import time
import os
import requests

#pylint: disable=import-error
if os.environ.get('SERVER_SOFTWARE','').startswith('Google'):
    import requests_toolbelt.adapters.appengine
    requests_toolbelt.adapters.appengine.monkeypatch()
#pylint: enable=import-error

import px_constants
import px_httpc
import px_utils

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
    """
    :param PxContext ctx:
    :param PxConfig config:
    :return dict:
    """
    start = time.time()
    body = prepare_risk_body(ctx, config)
    default_headers = {
        'Authorization': 'Bearer ' + config.auth_token,
        'Content-Type': 'application/json'
    }
    try:
        response = px_httpc.send(full_url=config.server_host + px_constants.API_RISK, body=json.dumps(body),
                                 config=config, headers=default_headers, method='POST', raise_error = True)
        if response:
            return json.loads(response.content)
        return False
    except requests.exceptions.Timeout:
        ctx.pass_reason = 's2s_timeout'
        risk_rtt = time.time() - start
        config.logger.debug('Risk API timed out, round_trip_time: {}'.format(risk_rtt))
        return False
    except requests.exceptions.RequestException as e:
        ctx.pass_reason = 's2s_error'
        config.logger.debug('Unexpected exception in Risk API call: {}'.format(e))
        return False

def verify(ctx, config):
    """
    :param PxContext ctx:
    :param pxConfig config:
    :return bool: is request verified
    """

    logger = config.logger
    logger.debug('Evaluating Risk API request, call reason: {}'.format(ctx.s2s_call_reason))
    try:
        start = time.time()
        response = send_risk_request(ctx, config)
        risk_rtt = time.time() - start
        logger.debug('Risk call took {} ms'.format(risk_rtt))

        if response:
            ctx.score = response.get('score')
            ctx.uuid = response.get('uuid')
            ctx.block_action = response.get('action')
            ctx.risk_rtt = risk_rtt
            ctx.pxde = response.get('data_enrichment', {})
            ctx.pxde_verified = True
            response_pxhd = response.get('pxhd', '')
            #Do not set cookie if there's already a valid pxhd
            ctx.response_pxhd = response_pxhd
            if ctx.score >= config.blocking_score:
                if response.get('action') == px_constants.ACTION_CHALLENGE and \
                        response.get('action_data') is not None and \
                        response.get('action_data').get('body') is not None:

                    logger.debug("received javascript challenge action")
                    ctx.block_action_data = response.get('action_data').get('body')
                    ctx.block_reason = 'challenge'

                elif response.get('action') is px_constants.ACTION_RATELIMIT:
                    logger.debug("received javascript ratelimit action")
                    ctx.block_reason = 'exceeded_rate_limit'

                else:
                    logger.debug("block score threshold reached, will initiate blocking")
                    ctx.block_reason = 's2s_high_score'
            else:
                ctx.pass_reason = 's2s'

            msg = 'Risk API response returned successfully, risk score: {}, round_trip_time: {} ms'
            logger.debug(msg.format(ctx.score, risk_rtt))
            return True
        else:
            return False
    except Exception as err:
        logger.error('Risk API request failed. Error: {}'.format(err))
        return False


def prepare_risk_body(ctx, config):
    logger = config.logger
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
        body['additional']['enforcer_vid_source'] = ctx.enforcer_vid_source
    if ctx.uuid:
        body['uuid'] = ctx.uuid
    if ctx.cookie_hmac:
        body['additional']['px_cookie_hmac'] = ctx.cookie_hmac
    if ctx.cookie_names:
        body['additional']['request_cookie_names'] = ctx.cookie_names
    if ctx.pxhd:
        body['pxhd'] = ctx.pxhd

    body = add_original_token_data(ctx, body)

    px_utils.prepare_custom_params(config, body['additional'])

    if ctx.s2s_call_reason == 'cookie_decryption_failed':
        logger.debug('attaching orig_cookie to request')
        body['additional']['px_cookie_raw'] = ctx.px_cookie_raw

    if ctx.s2s_call_reason in ['cookie_expired', 'cookie_validation_failed']:
        logger.debug('attaching px_cookie to request')
        body['additional']['px_cookie'] = ctx.decoded_cookie

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
