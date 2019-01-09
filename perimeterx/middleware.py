import time

from werkzeug.wrappers import Request

import px_activities_client
from px_config import PxConfig
from px_context import PxContext
from px_request_verifier import PxRequestVerifier


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
        self._config = px_config
        self._request_verifier = PxRequestVerifier(px_config)
        px_activities_client.init_activities_configuration(px_config)
        px_activities_client.send_enforcer_telemetry_activity(config=px_config, update_reason='initial_config')

    def __call__(self, environ, start_response):
        try:
            start = time.time()
            context = None

            if environ.get('px_disable_request'):
                return self.app(environ, start_response)

            request = Request(environ)
            context, verified_response = self.verify(request)
            self._config.logger.debug("PerimeterX Enforcer took: {} ms".format((time.time() - start) * 1000))
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
            if not config._module_enabled:
                logger.debug('Request will not be verified, module is disabled')
                return ctx, True
            ctx = PxContext(request, config)
            return ctx, self._request_verifier.verify_request(ctx, request)
        except Exception as err:
            logger.error("Caught exception, passing request. Exception: {}".format(err))
            if ctx:
                self.report_pass_traffic(ctx)
            else:
                self.report_pass_traffic(PxContext({}, config))
            return True


    def report_pass_traffic(self, ctx):
        px_activities_client.send_page_requested_activity(ctx, self.config)

    def report_block_traffic(self, ctx):
        px_activities_client.send_block_activity(ctx, self.config)

    @property
    def config(self):
        return self._config




