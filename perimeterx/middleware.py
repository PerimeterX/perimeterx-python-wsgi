import time

from werkzeug.wrappers import Request, Response

import px_activities_client
import px_api
import px_blocker
import px_constants
import px_cookie_validator
import px_utils
from perimeterx.px_proxy import PXProxy
from px_config import PxConfig
from px_context import PxContext


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
        self._module_enabled = self._config.module_enabled
        px_activities_client.init_activities_configuration(px_config)
        px_activities_client.send_enforcer_telemetry_activity(config=px_config, update_reason='initial_config')

    def __call__(self, environ, start_response):
        try:
            start = time.time()
            context = None
            request = Request(environ)
            context, verified_response = self.verify(request)
            self._config.logger.debug("PerimeterX Enforcer took: {} ms".format(time.time() - start))
            if verified_response is True:
                return self.app(environ, start_response)

            return verified_response(environ, start_response)

        except Exception as err:
            self._config.logger.error("Caught exception, passing request. Exception: {}".format(err))
            if context:
                self.report_pass_traffic(context)
            else:
                self.report_pass_traffic(PxContext({}, self._config))
            return self.app(environ, start_response)

    def verify(self, request):
        config = self.config
        logger = config.logger
        logger.debug('Starting request verification')
        ctx = None
        try:
            if not self._module_enabled:
                logger.debug('Request will not be verified, module is disabled')
                return ctx, True
            ctx = PxContext(request, config)
            return ctx, self.verify_request(ctx, request)
        except Exception as err:
            logger.error("Caught exception, passing request. Exception: {}".format(err))
            if ctx:
                self.report_pass_traffic(ctx)
            else:
                self.report_pass_traffic(PxContext({}, config))
            return True

    def verify_request(self, ctx, request):
        logger = self._config.logger
        uri = ctx.uri
        px_proxy = PXProxy(self.config)
        if px_proxy.should_reverse_request(uri):
            return px_proxy.handle_reverse_request(self.config, ctx, request.data)
        if px_utils.is_static_file(ctx):
            logger.debug('Filter static file request. uri: {}'.format(uri))
            return True
        if ctx.whitelist_route:
            logger.debug('The requested uri is whitelisted, passing request')
            return True
        # PX Cookie verification
        if not px_cookie_validator.verify(ctx, self.config):
            # Server-to-Server verification fallback
            if not px_api.verify(ctx, self.config):
                return True
        return self.handle_verification(ctx, self.config, request)



    def handle_verification(self, ctx, config, request):
        logger = config.logger
        ctx.score = 100
        score = ctx.score
        data = None
        headers = None
        status = None
        pass_request = False
        if score < config.blocking_score:
            logger.debug('Risk score is lower than blocking score')
            self.report_pass_traffic(ctx)
            pass_request = True
        else:
            logger.debug('Risk score is higher or equal than blocking score')
            self.report_block_traffic(ctx)
            if config.additional_activity_handler:
                config.additional_activity_handler(ctx, config)
            if config.module_mode == px_constants.MODULE_MODE_BLOCKING:
                data, headers, status = self.px_blocker.handle_blocking(ctx=ctx, config=config)
            response_function = generate_blocking_response(data, headers, status)

        if config.custom_request_handler:
            data, headers, status = config.custom_request_handler(ctx, self.config, request)
            if data and headers and status:
                return generate_blocking_response(data, headers, status)

        if pass_request:
            return True
        else:
            return response_function

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

    def disable_module(self):
        if not self._module_enabled:
            self._config.logger.debug("Trying to disable the module, module already disabled")
        else:
            self._module_enabled = False

    def enable_module(self):
        if self._module_enabled:
            self._config.logger.debug("Trying to enable the module, module already enabled")
        else:
            self._module_enabled = True



def generate_blocking_response(data, headers, status):
    result = Response(data)
    result.headers = headers
    result.status = status
    return result
