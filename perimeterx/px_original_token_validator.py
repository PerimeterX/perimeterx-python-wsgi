import traceback
import re

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
        logger.debug('Original token found, Evaluating');

        px_cookie = PxTokenV3(ctx, config, ctx["original_token"])

    except Exception, e:
        traceback.print_exc()
        logger.debug('Could not decrypt original token, exception was thrown, decryption failed ' + e.message)
        return False
