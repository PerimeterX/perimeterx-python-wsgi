import json

import px_constants


def testing_mode_handling(ctx, config, request):
    result = {
        'px_cookies': ctx.px_cookies,
        'vid': ctx.vid,
        'ip': ctx.ip,
        'full_url': ctx.full_url,
        'px_cookie_hmac': ctx.cookie_hmac,
        'block_action': ctx.block_action,
        'http_method': ctx.http_method,
        'hostname': ctx.hostname,
        'headers': dict(ctx.headers),
        'user_agent': ctx.user_agent,
        'uri': ctx.uri,
        'is_made_s2s_api_call': True if ctx.s2s_call_reason != 'none' else False,
        'sensitive_route': ctx.sensitive_route,
        'decoded_px_cookie': ctx.decoded_cookie,
        'cookie_origin': ctx.cookie_origin,
        'http_version': ctx.http_version,
        's2s_call_reason': ctx.s2s_call_reason,
        'block_reason': ctx.block_reason,
        'module_mode': 1 if config.module_mode is px_constants.MODULE_MODE_BLOCKING else 0,
        'score': ctx.score,
        'risk_rtt': ctx.risk_rtt,
        'uuid': ctx.uuid,
        'pxde': ctx.pxde,
        'pxde_verified': ctx.pxde_verified,
    }

    if ctx.original_uuid:
        result['original_uuid'] = ctx.original_uuid
    if ctx.original_token_error:
        result['original_token_error'] = ctx.original_token_error

    return json.dumps(result), {'Content-Type': 'application/json'}, '200 OK'
