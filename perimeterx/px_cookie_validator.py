import traceback

from perimeterx import px_constants


def verify(ctx, config):
    """
    main verification function, verifying the content of the perimeterx risk cookie if exists
    :param ctx: perimeterx request context object
    :param config: global configurations
    :type ctx: dictionary
    :type config: dictionary
    :return: Returns True if verification succeeded and False if not
    :rtype: Bool
    """
    logger = config['logger']
    try:
        if not ctx["px_cookies"].keys():
            logger.debug('No risk cookie on the request')
            ctx['s2s_call_reason'] = 'no_cookie'
            return False

        from px_cookie import PxCookie
        px_cookie = PxCookie.build_px_cookie(ctx, config)

        if not px_cookie.deserialize():
            logger.error('Cookie decryption failed')
            ctx['px_orig_cookie'] = px_cookie.raw_cookie
            ctx['s2s_call_reason'] = 'cookie_decryption_failed'
            return False

        ctx['risk_score'] = px_cookie.get_score()
        ctx['uuid'] = px_cookie.get_uuid()
        ctx['vid'] = px_cookie.get_vid()
        ctx['decoded_cookie'] = px_cookie.decoded_cookie
        ctx['cookie_hmac'] = px_cookie.get_hmac()
        ctx['block_action'] = px_cookie.get_action()

        if px_cookie.is_high_score():
            ctx['block_reason'] = 'cookie_high_score'
            logger.debug('Cookie with high score: ' + str(ctx['risk_score']))
            return True

        if px_cookie.is_cookie_expired():
            ctx['s2s_call_reason'] = 'cookie_expired'
            logger.debug('Cookie expired')
            return False

        if not px_cookie.is_secured():
            logger.debug('Cookie validation failed')
            ctx['s2s_call_reason'] = 'cookie_validation_failed'
            return False

        if ctx.get('is_sensitive_route',False):
            logger.debug('Cookie validation passed but is on sensitive route')
            ctx['s2s_call_reason'] = 'sensitive_route'
            return False

        ctx['pass_reason'] = px_constants.PASS_REASON_COOKIE
        logger.debug('Cookie validation passed with good score: ' + str(ctx['risk_score']))
        return True
    except Exception, e:
        traceback.print_exc()
        logger.debug('Could not decrypt cookie, exception was thrown, decryption failed ' + e.message)
        ctx['px_orig_cookie'] = px_cookie.raw_cookie
        ctx['s2s_call_reason'] = 'cookie_decryption_failed'
        return False
