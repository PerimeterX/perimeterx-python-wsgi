import px_activities_client
import px_cookie_validator
from px_context import PxContext
import px_blocker
import px_api
import px_constants
import px_utils
from perimeterx.px_proxy import PXProxy
from px_config import PxConfig


class PerimeterX(object):
    def __init__(self, app, config=None):
        self.app = app
        # merging user's defined configurations with the default one
        px_config = PxConfig(config)
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
        self._PXBlocker = px_blocker.PXBlocker()
        self._config = px_config
        px_activities_client.init_activities_configuration(px_config)
        px_activities_client.send_enforcer_telemetry_activity(config=px_config, update_reason='initial_config')

    def __call__(self, environ, start_response):
        return self._verify(environ, start_response)

    def _verify(self, environ, start_response):
        config = self.config
        logger = config.logger
        try:
            ctx = PxContext(environ, config)
            uri = ctx.uri
            px_proxy = PXProxy(config)
            if px_proxy.should_reverse_request(uri):
                body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH'))) if environ.get(
                    'CONTENT_LENGTH') else ''
                return px_proxy.handle_reverse_request(self.config, ctx, start_response, body)
            if px_utils.is_static_file(ctx):
                logger.debug('Filter static file request. uri: ' + uri)
                return self.app(environ, start_response)
            if not self._config._module_enabled:
                logger.debug('Module is disabled, request will not be verified')
                return self.app(environ, start_response)

            if ctx.whitelist_route:
                logger.debug('The requested uri is whitelisted, passing request')
                return self.app(environ, start_response)

            # PX Cookie verification
            if not px_cookie_validator.verify(ctx, config):
                # Server-to-Server verification fallback
                if not px_api.verify(ctx, self.config):
                    return self.app(environ, start_response)
            return self.handle_verification(ctx, self.config, environ, start_response)
        except:
            logger.error("Caught exception, passing request")
            self.pass_traffic(PxContext({}, config))
            return self.app(environ, start_response)

    def handle_verification(self, ctx, config, environ, start_response):
        score = ctx.score
        result = None
        headers = None
        status = None
        pass_request = True
        if score < config.blocking_score:
            self.pass_traffic(ctx)
        else:
            pass_request = False
            self.block_traffic(ctx)

        if config.additional_activity_handler:
            config.additional_activity_handler(ctx, config)

        if config.module_mode == px_constants.MODULE_MODE_BLOCKING and result is None and not pass_request:
            result, headers, status = self.px_blocker.handle_blocking(ctx=ctx, config=config)
        if config.custom_request_handler:
            custom_body, custom_headers, custom_status = config.custom_request_handler(ctx, self.config, environ)
            if custom_body is not None:
                start_response(custom_status, custom_headers)
                return custom_body

        if headers is not None:
            start_response(status, headers)
            return result
        else:
            return self.app(environ, start_response)

    def pass_traffic(self, ctx):
        px_activities_client.send_page_requested_activity(ctx, self.config)

    def block_traffic(self, ctx):
        px_activities_client.send_block_activity(ctx, self.config)

    @property
    def config(self):
        return self._config

    @property
    def px_blocker(self):
        return self._PXBlocker
