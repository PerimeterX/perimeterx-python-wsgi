"""
PerimeterX example app implemented in a google app engine based environment
"""

import webapp2
from perimeterx.middleware import PerimeterX


class MainPage(webapp2.RequestHandler):
    def get(self):
        index_html = open('index.html').read()
        self.response.out.write(index_html)


def ip_handler(environ):
    for key in environ.keys():
        if key == 'HTTP_X_FORWARDED_FOR':
            xff = environ[key].split(' ')[1]
            return xff
    return '1.2.3.4'


def custom_block_handler(ctx, start_response):
    uuid = ctx.get('uuid')
    block_score = ctx.get('risk_score')
    vid = ctx.get('vid')
    app_id = 'PX_APP_ID'
    captcha = True
    html_head = '<html lang="en"><head><script src="https://www.google.com/recaptcha/api.js"></script>'
    captcha_code = '<script> function handleCaptcha(response) {' \
                   ' var name = \'_pxCaptcha\'; var expiryUtc = new Date(Date.now() + 1000 * 10).toUTCString(); ' \
                   'var cookieParts = [name, \'=\', response + \':\' + ' + vid + ':' + uuid + '; expires=\', expiryUtc, \'; path=/\'];' \
                                                                                              ' document.cookie = cookieParts.join(\'\'); location.reload(); } </script>'

    body_start = '<body> You have been blocked!'
    body_captcha = '<br/><div class="g-recaptcha" data-sitekey="6Lcj-R8TAAAAABs3FrRPuQhLMbp5QrHsHufzLf7b" data-callback="handleCaptcha" data-theme="dark"></div> <br><span style="font-size: 20px;">'
    px_snippet = '<script type="text/javascript"> (function(){ window._pxAppId="' + app_id + '"; var p=document.getElementsByTagName("script")[0], s=document.createElement("script"); s.async=1; s.src="//client.perimeterx.net/' + app_id + '/main.min.js"; p.parentNode.insertBefore(s,p); }()); </script>'
    body_end = '<br/>Block Reference: <span style="color: #525151;">#' + uuid + '</span></span> </div> </body> </html>'

    print 'user id: ' + vid + ' blocked with score: ' + str(block_score) + ' ref: #' + uuid
    if captcha:
        custom_block_page = html_head + captcha_code + body_start + body_captcha + px_snippet + body_end
    else:
        custom_block_page = html_head + body_start + px_snippet + body_end

    start_response('403 Forbidden', [('Content-Type', 'text/html')])
    return [custom_block_page]


px_config = {
    'app_id': 'PX_APP_ID',
    'cookie_key': 'PX_COOKIE_KEY',
    'auth_token': 'PX_AUTH_TOKEN',
    'blocking_score': 70,
    'debug_mode': True,
    'ip_handler': ip_handler,
    'captcha_enabled': True,
    'custom_block_handler': custom_block_handler,
    'module_mode': 'active_blocking'
}

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
app = PerimeterX(app, px_config)
