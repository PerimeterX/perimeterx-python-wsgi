from px_logger import Logger
import px_context
import px_activities_client
import px_cookie
import px_httpc
import px_captcha
import px_api
import px_template
import Cookie



class PerimeterX(object):
    def __init__(self, app, config=None):
        self.app = app
        # merging user's defined configurations with the default one
        self.config = {
            'blocking_score': 60,
            'debug_mode': False,
            'module_version': 'Python SDK v1.0.3',
            'module_mode': 'active_monitoring',
            'perimeterx_server_host': 'sapi.perimeterx.net',
            'captcha_enabled': True,
            'server_calls_enabled': True,
            'sensitive_headers': ['cookie', 'cookies'],
            'send_page_activities': True,
            'api_timeout': 1,
            'custom_logo': None,
            'css_ref': None,
            'js_ref': None
        }

        self.config = dict(self.config.items() + config.items())
        self.config['logger'] = logger = Logger(self.config['debug_mode'])
        if not config['app_id']:
            logger.error('PX App ID is missing')
            raise ValueError('PX App ID is missing')

        # if APP_ID is not set, use the deafult perimeterx server - else, use the appid specific sapi.
        self.config['perimeterx_server_host'] = 'sapi.perimeterx.net' if self.config['app_id'] == 'PX_APP_ID' else 'sapi-' + self.config['app_id'].lower() + '.perimeterx.net'
        if not config['auth_token']:
            logger.error('PX Auth Token is missing')
            raise ValueError('PX Auth Token is missing')

        if not config['cookie_key']:
            logger.error('PX Cookie Key is missing')
            raise ValueError('PX Cookie Key is missing')

        px_httpc.init(self.config)

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            cookies = Cookie.SimpleCookie(environ.get('HTTP_COOKIE'))
            if cookies.get('_pxCaptcha') and cookies.get('_pxCaptcha').value:
                cookie = Cookie.SimpleCookie()
                cookie['_pxCaptcha'] = '';
                cookie['_pxCaptcha']['expires'] = 'Expires=Thu, 01 Jan 1970 00:00:00 GMT';
                headers.append(('Set-Cookie', cookie['_pxCaptcha'].OutputString()))
                self.config['logger'].debug('Cleared Cookie');
            return start_response(status, headers, exc_info)

        return self._verify(environ, custom_start_response)

    def _verify(self, environ, start_response):
        logger = self.config['logger']
        ctx = px_context.build_context(environ, self.config)

        if ctx.get('module_mode') == 'inactive' or is_static_file(ctx):
            logger.debug('Filter static file request. uri: ' + ctx.get('uri'))
            return self.app(environ, start_response)

        cookies = Cookie.SimpleCookie(environ.get('HTTP_COOKIE'))
        if self.config.get('captcha_enabled') and cookies.get('_pxCaptcha') and cookies.get('_pxCaptcha').value:
            pxCaptcha = cookies.get('_pxCaptcha').value
            if px_captcha.verify(ctx, self.config, pxCaptcha):
                logger.debug('User passed captcha verification. user ip: ' + ctx.get('socket_ip'))
                return self.app(environ, start_response)

        # PX Cookie verification
        if not px_cookie.verify(ctx, self.config) and self.config.get('server_calls_enabled', True):
            # Server-to-Server verification fallback
            if not px_api.verify(ctx, self.config):
                return self.app(environ, start_response)

        return self.handle_verification(ctx, self.config, environ, start_response)

    def handle_verification(self, ctx, config, environ, start_response):
        score = ctx.get('risk_score', -1)

        if score < config['blocking_score']:
            return self.pass_traffic(environ, start_response, ctx)

        if config.get('custom_block_handler', False):
            px_activities_client.send_block_activity(ctx, config)
            return config['custom_block_handler'](ctx, start_response)
        elif config.get('module_mode', 'active_monitoring') == 'active_blocking':
            vid = ctx.get('vid', '')
            uuid = ctx.get('uuid', '')
            template = 'block'
            if config.get('captcha_enabled', False):
                template = 'captcha'

            body = px_templates.get_template(self.config, uuid, vid)

            px_activities_client.send_block_activity(ctx, config)
            start_response("403 Forbidden", [('Content-Type', 'text/html')])
            return [str(body)]
        else:
            return self.pass_traffic(environ, start_response, ctx)

    def pass_traffic(self, environ, start_response, ctx):
        details = {}
        if(ctx['decoded_cookie']):
            details = {"px_cookie": ctx['decoded_cookie']}
        px_activities_client.send_to_perimeterx('page_requested', ctx, self.config, details)
        return self.app(environ, start_response)


def is_static_file(ctx):
    uri = ctx.get('uri', '')
    static_extensions = ['.css', '.bmp', '.tif', '.ttf', '.docx', '.woff2', '.js', '.pict', '.tiff', '.eot',
                         '.xlsx', '.jpg', '.csv', '.eps', '.woff', '.xls', '.jpeg', '.doc', '.ejs', '.otf', '.pptx',
                         '.gif', '.pdf', '.swf', '.svg', '.ps', '.ico', '.pls', '.midi', '.svgz', '.class', '.png',
                         '.ppt', '.mid', 'webp', '.jar']

    for ext in static_extensions:
        if uri.endswith(ext):
            return True
    return False
