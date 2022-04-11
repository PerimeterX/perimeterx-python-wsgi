import re
import traceback

import px_original_token_validator
from px_config import PxConfig
from px_context import PxContext
from px_cookie import PxCookie

mobile_error_pattern = re.compile("^\d+$")


def verify(ctx, config):
    """
    main verification function, verifying the content of the perimeterx risk cookie if exists
    :param PxContext ctx: perimeterx request context object
    :param PxConfig config: global configurations
    :return Bool: Returns True if verification succeeded and False if not
    """
    logger = config.logger
    try:
        if not ctx.px_cookies.keys():
            logger.debug('Cookie is missing')
            ctx.s2s_call_reason = 'no_cookie'
            return False

        if not config.cookie_key:
            logger.debug('No cookie key found, stopping cookie evaluation')
            ctx['s2s_call_reason'] = 'no_cookie_key'
            return False

        px_cookie_builder = PxCookie(config)

        cookie_version, px_cookie = px_cookie_builder.build_px_cookie(px_cookies=ctx.px_cookies,
                                                      user_agent=ctx.user_agent)
        # Mobile SDK traffic
        if px_cookie and ctx.is_mobile:
            if re.match(mobile_error_pattern, px_cookie._raw_cookie):
                logger.debug('Mobile special token - {}'.format(px_cookie.raw_cookie))
                ctx.s2s_call_reason = "mobile_error_" + px_cookie.raw_cookie
                if ctx.original_token is not None:
                    px_original_token_validator.verify(ctx, config)

                return False
            else:
                logger.debug('Mobile special token - no token')

        if not px_cookie.deserialize():
            cookie = px_cookie._hmac + ":" + px_cookie._raw_cookie
            logger.debug('Cookie decryption failed, value: {}'.format(cookie))
            ctx.px_cookie_raw = cookie_version + "=" + cookie
            ctx.s2s_call_reason = 'cookie_decryption_failed'
            return False

        ctx.score = px_cookie.get_score()
        ctx.uuid = px_cookie.get_uuid()
        if px_cookie.get_vid():
            ctx.vid = px_cookie.get_vid()
            ctx.enforcer_vid_source = 'risk_cookie'
        ctx.decoded_cookie = px_cookie.decoded_cookie
        ctx.cookie_hmac = px_cookie.get_hmac()
        ctx.block_action = px_cookie.get_action()

        if px_cookie.is_high_score():
            ctx.block_reason = 'cookie_high_score'
            logger.debug('Cookie with high score: {}'.format(ctx.score))
            return True

        if px_cookie.is_cookie_expired():
            ctx.s2s_call_reason = 'cookie_expired'
            msg = 'Cookie TTL is expired, value: {}, age: {}'
            logger.debug(msg.format(px_cookie.decoded_cookie, px_cookie.get_age()))
            return False

        if not px_cookie.is_secured():
            msg = 'Cookie HMAC validation failed, value: {}, user-agent: {}'
            logger.debug(msg.format(px_cookie.decoded_cookie, px_cookie._user_agent))
            ctx.s2s_call_reason = 'cookie_validation_failed'
            return False

        if ctx.sensitive_route:
            logger.debug('Sensitive route match, sending Risk API. path: {}'.format(ctx.uri))
            ctx.s2s_call_reason = 'sensitive_route'
            return False

        logger.debug('Cookie evaluation ended successfully, risk score: {}'.format(ctx.score))
        return True
    except Exception, err:
        traceback.print_exc()
        logger.error('Unexpected exception while evaluating Risk cookie. Error: {}'.format(err))
        ctx.px_cookie_raw = px_cookie._raw_cookie
        ctx.s2s_call_reason = 'cookie_decryption_failed'
        return False
