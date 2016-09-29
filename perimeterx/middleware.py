from px_logger import Logger
import px_context
import px_activities_client
import px_cookie
import px_httpc
import px_captcha
import px_api


class PerimeterX(object):
    def __init__(self, app, config=None):
        self.app = app
        # merging user's defined configurations with the default one
        self.config = {
            'blocking_score': 60,
            'debug_mode': False,
            'module_version': 'Python SDK v1.0.2',
            'module_mode': 'active_monitoring',
            'perimeterx_server_host': 'sapi.perimeterx.net',
            'captcha_enabled': True,
            'sensitive_headers': ['cookie', 'cookies'],
            'send_page_activities': False,
            'api_timeout': 1
        }

        self.config = dict(self.config.items() + config.items())
        self.config['logger'] = logger = Logger(self.config['debug_mode'])

        if not config['app_id']:
            logger.error('PX App ID is missing')
            raise ValueError('PX App ID is missing')

        if not config['auth_token']:
            logger.error('PX Auth Token is missing')
            raise ValueError('PX Auth Token is missing')

        if not config['cookie_key']:
            logger.error('PX Cookie Key is missing')
            raise ValueError('PX Cookie Key is missing')

        px_httpc.init(self.config)

    def __call__(self, environ, start_response):
        return self._verify(environ, start_response)

    def _verify(self, environ, start_response):
        logger = self.config['logger']
        ctx = px_context.build_context(environ, self.config)

        if ctx.get('module_mode') == 'inactive' or is_static_file(ctx):
            logger.debug('Filter static file request. uri: ' + ctx.get('uri'))
            return self.app(environ, start_response)

        if ctx['px_captcha'] and self.config['captcha_enabled'] and px_captcha.verify(ctx, self.config):
            logger.debug('User passed captcha verification. user ip: ' + ctx.get('socket_ip') )
            return self.app(environ, start_response)

        if not px_cookie.verify(ctx, self.config):
            if not px_api.verify(ctx, self.config):
                return self.app(environ, start_response)

        return self.handle_verification(ctx, self.config, environ, start_response)

    def handle_verification(self, ctx, config, environ, start_response):
        score = ctx.get('risk_score', 0)

        if score < config['blocking_score']:
            return self.pass_traffic(environ, start_response, ctx)

        if config.get('custom_block_handler', False):
            px_activities_client.send_block_activity(ctx, config)
            return config['custom_block_handler'](ctx, start_response)
        elif config.get('module_mode', 'active_monitoring') == 'active_blocking':
            vid = ctx.get('vid', '')
            uuid = ctx.get('uuid', '')
            app_id = config.get('app_id', '')

            html_head = '<html lang="en"> <head> <link type="text/css" rel="stylesheet" media="screen, print" href="//fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,800italic,400,300,600,700,800"> <meta charset="UTF-8"> <title>Access to This Page Has Been Blocked</title> <style> p { width: 60%; margin: 0 auto; font-size: 35px; } ' \
                        'body { background-color: #a2a2a2; font-family: "Open Sans"; margin: 5%; } img { width: 180px; } a { color: #2020B1; text-decoration: blink; }' \
                        ' a:hover { color: #2b60c6; } </style> <script src="https://www.google.com/recaptcha/api.js"></script>'
            captcha = '<script> window.px_vid = "' + vid + '" ; function handleCaptcha(response) {' \
                                                           ' var name = \'_pxCaptcha\'; var expiryUtc = new Date(Date.now() + 1000 * 10).toUTCString(); ' \
                                                           'var cookieParts = [name, \'=\', response + \':\' + window.px_vid, \'; expires=\', expiryUtc, \'; path=/\'];' \
                                                           ' document.cookie = cookieParts.join(\'\'); location.reload(); } </script>'

            body_start = '<body cz-shortcut-listen="true"> <div><img src="http://storage.googleapis.com/instapage-thumbnails/035ca0ab/e94de863/1460594818-1523851-467x110-perimeterx.png"> ' \
                         '</div> <span style="color: white; font-size: 34px;">Access to This Page Has Been Blocked</span> <div style="font-size: 24px;color: #000042;">' \
                         '<br> Access is blocked according to the site security policy.<br> Your browsing behaviour fingerprinting made us think you may be a bot. <br>' \
                         '<br> This may happen as a result ofthe following: <ul> <li>JavaScript is disabled or not running properly.</li> ' \
                         '<li>Your browsing behaviour fingerprinting are not likely to be a regular user.</li> </ul> To read more about the bot defender solution: ' \
                         '<a href="https://www.perimeterx.com/bot-defender">https://www.perimeterx.com/bot-defender</a><br> If you think the blocking was done by mistake, ' \
                         'contact the site administrator. <br/>'
            body_captcha = '<br/><div class="g-recaptcha" data-sitekey="6Lcj-R8TAAAAABs3FrRPuQhLMbp5QrHsHufzLf7b" data-callback="handleCaptcha" data-theme="dark"></div> <br><span style="font-size: 20px;">'
            px_snippet = '<script type="text/javascript"> (function(){ window._pxAppId="' + app_id + '"; var p=document.getElementsByTagName("script")[0], s=document.createElement("script"); s.async=1; s.src="//client.perimeterx.net/' + app_id + '/main.min.js"; p.parentNode.insertBefore(s,p); }()); </script>'
            body_end = '<br/>Block Reference: <span style="color: #525151;">#' + uuid + '</span></span> </div> </body> </html>'

            if config.get('captcha_enabled', False):
                body = html_head + px_snippet + captcha + body_start + body_captcha + body_end
            else:
                body = html_head + px_snippet + body_start + body_end

            px_activities_client.send_block_activity(ctx, config)
            start_response("403 Forbidden", [('Content-Type', 'text/html')])
            return [str(body)]
        else:
            return self.pass_traffic(environ, start_response, ctx)

    def pass_traffic(self, environ, start_response, ctx):
        px_activities_client.send_to_perimeterx('page_requested', ctx, self.config, {})
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
