from px_cookie import PxCookie


def verify(ctx, config):
    """
    main verification function, verifying the content of the perimeterx original token risk if exists
    :param pxContext ctx: perimeterx request context object
    :param PxConfig config: global configurations
    :return bool: Returns True if verification succeeded and False if not
    """
    logger = config.logger
    try:
        logger.debug('Original token found, Evaluating')
        original_token = ctx.original_token
        version, no_version_token = original_token.split(':', 1)
        px_cookie_builder = PxCookie(config)
        cookie_version, px_cookie = px_cookie_builder.build_px_cookie({version: no_version_token}, '')

        if not px_cookie.deserialize():
            logger.debug('Original token decryption failed, value: {}'.format(px_cookie.raw_cookie))
            ctx.original_token_error = 'decryption_failed'
            return False

        ctx.decoded_original_token = px_cookie.decoded_cookie
        ctx.vid = px_cookie.get_vid()
        ctx.original_uuid = px_cookie.get_uuid()
        if not px_cookie.is_secured():
            logger.debug('Original token HMAC validation failed, value: {}'.format(px_cookie.decoded_cookie))
            ctx.original_token_error = 'validation_failed'
            return False
        return True

    except Exception, e:
        logger.debug('Could not decrypt original token, exception was thrown, decryption failed. Error: {}'.format(e.message))
        ctx.original_token_error = 'decryption_failed'
        return False
