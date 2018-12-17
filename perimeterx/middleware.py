import px_activities_client
import px_cookie_validator
from px_context import PxContext
import px_blocker
import px_api
import px_constants
import px_utils
from perimeterx.px_proxy import PXProxy
from px_config import PxConfig
from werkzeug.wrappers import Request, Response


class PerimeterX(object):
    def __init__(self, app, config=None):
        self.app = app
        # merging user's defined configurations with the default one
        px_config = PxConfig(config)
        logger = px_config.logger

        if not px_config.app_id:
            logger.error('Unable to initialize module, missing mandatory configuration: app_id')
            raise ValueError('PX App ID is missing')

        if not px_config.auth_token:
            logger.error('Unable to initialize module, missing mandatory configuration: auth_token')
            raise ValueError('PX Auth Token is missing')

        if not px_config.cookie_key:
            logger.error('Unable to initialize module, missing mandatory configuration: px_cookie')
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
        logger.debug('Starting request verification')
        request = Request(environ)
        try:
            if not self._config.module_enabled:
                logger.debug('Request will not be verified, module is disabled')
                return self.app(environ, start_response)
            ctx = PxContext(request, config)
            uri = ctx.uri
            px_proxy = PXProxy(config)

            if px_proxy.should_reverse_request(uri):
                return px_proxy.handle_reverse_request(self.config, ctx, start_response, request.data, environ)
            if px_utils.is_static_file(ctx):
                logger.debug('Filter static file request. uri: {}'.format(uri))
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
        except Exception as err:
            logger.error("Caught exception, passing request. Exception: {}".format(err))
            if ctx:
                self.report_pass_traffic(ctx)
            else:
                self.report_pass_traffic(PxContext({}, config))
            return self.app(environ, start_response)

    def handle_verification(self, ctx, config, environ, start_response):
        logger = config.logger
        score = ctx.score
        data = None
        headers = None
        status = None
        if score < config.blocking_score:
            logger.debug('Risk score is lower than blocking score')
            self.report_pass_traffic(ctx)
            return self.app(environ, start_response)
        else:
            logger.debug('Risk score is higher or equal than blocking score')
            self.report_block_traffic(ctx)
            if config.additional_activity_handler:
                config.additional_activity_handler(ctx, config)
            if config.module_mode == px_constants.MODULE_MODE_BLOCKING:
                data, headers, status = self.px_blocker.handle_blocking(ctx=ctx, config=config)
            if config.custom_request_handler:
                data, headers, status = config.custom_request_handler(ctx, self.config, environ)
            response = Response(data)
            response.headers = headers
            response.status = status
            return response(environ, start_response)

    def report_pass_traffic(self, ctx):
        px_activities_client.send_page_requested_activity(ctx, self.config)

    def report_block_traffic(self, ctx):
        px_activities_client.send_block_activity(ctx, self.config)

    @property
    def config(self):
        return self._config

    @property
    def px_blocker(self):
        return self._PXBlocker
