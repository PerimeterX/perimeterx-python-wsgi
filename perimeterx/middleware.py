import px_context
import px_activities_client
import px_cookie_validator
import px_httpc
import px_blocker
import px_api
import px_constants
import px_utils
from px_proxy import PXProxy
from px_config import PXConfig


class PerimeterX(object):
    def __init__(self, app, config=None):
        self.app = app
        # merging user's defined configurations with the default one
        px_config = PXConfig(config)
        logger = px_config.logger
        if not px_config.app_id:
            logger.error('PX App ID is missing')
            raise ValueError('PX App ID is missing')

        # if APP_ID is not set, use the deafult perimeterx server - else, use the appid specific sapi.
        if not px_config.auth_token:
            logger.error('PX Auth Token is missing')
            raise ValueError('PX Auth Token is missing')

        if not px_config.cookie_key:
            logger.error('PX Cookie Key is missing')
            raise ValueError('PX Cookie Key is missing')
        self.reverse_proxy_prefix = px_config.app_id[2:].lower()
        if px_config.custom_request_handler:
             self.handle_verification = px_config.custom_request_handler.__get__(self, PerimeterX)
        self._PXBlocker = px_blocker.PXBlocker()
        self._config = px_config
        px_httpc.init(px_config)

    def __call__(self, environ, start_response):
        return self._verify(environ, start_response)

    def _verify(self, environ, start_response):
        config = self.config
        logger = config.logger
        try:
            ctx = px_context.build_context(environ, config)
            uri = ctx.get('uri')
            px_proxy = PXProxy(config)
            if px_proxy.should_reverse_request(uri):
                return px_proxy.handle_reverse_request(self.config, ctx, start_response)
            if px_utils.is_static_file(ctx):
                logger.debug('Filter static file request. uri: ' + uri)
                return self.app(environ, start_response)
            if not self._config._module_enabled:
                logger.debug('Module is disabled, request will not be verified')
                return self.app(environ, start_response)

            # PX Cookie verification
            if not px_cookie_validator.verify(ctx, config):
                # Server-to-Server verification fallback
                if not px_api.verify(ctx, self.config):
                    return self.app(environ, start_response)
            if config.custom_request_handler:
                return config.custom_request_handler(ctx, self.config, environ, start_response)
            return self.handle_verification(ctx, self.config, environ, start_response)
        except:
            logger.error("Cought exception, passing request")
            self.pass_traffic(environ, start_response, ctx)

    def handle_verification(self, ctx, config, environ, start_response):
        score = ctx.get('risk_score', -1)

        if score < config.blocking_score:
            return self.pass_traffic(environ, start_response, ctx)

        if config.custom_block_handler:
            px_activities_client.send_block_activity(ctx, config)
            return config.custom_block_handler(ctx, start_response)
        elif config.module_mode == px_constants.MODULE_MODE_BLOCKING:
            return self.px_blocker.handle_blocking(ctx=ctx, config=config, start_response=start_response)
        else:
            return self.pass_traffic(environ, start_response, ctx)

    def pass_traffic(self, environ, start_response, ctx):
        details = {}
        if ctx.get('decoded_cookie', ''):
            details = {"px_cookie": ctx['decoded_cookie']}
        px_activities_client.send_to_perimeterx(px_constants.PAGE_REQUESTED_ACTIVITY, ctx, self.config, details)
        return self.app(environ, start_response)

    @property
    def config(self):
        return self._config

    @property
    def px_blocker(self):
        return self._PXBlocker



