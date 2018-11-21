import pystache
import px_template
import px_constants


class PXBlocker(object):
    def __init__(self):
        self.mustache_renderer = pystache.Renderer()
        self.ratelimit_rendered_page = self.mustache_renderer.render(
            px_template.get_template(px_constants.RATELIMIT_TEMPLATE), {})

    def handle_blocking(self, ctx, config, start_response):
        action = ctx.get('block_action')
        status = '403 Forbidden'
        if action is 'j':
            blocking_response = ctx['block_action_data']
        elif action is 'r':
            blocking_response = self.ratelimit_rendered_page
            status = '429 Too Many Requests'
        else:
            blocking_props = self.prepare_properties(ctx, config)
            blocking_response = self.mustache_renderer.render(px_template.get_template(px_constants.BLOCK_TEMPLATE), blocking_props)
        is_json_response = self.is_json_response(ctx)
        if is_json_response:
            content_type = 'application/json'
        else:
            content_type = 'text/html'

        headers = [('Content-Type', content_type)]
        start_response(status, headers)
        return str(blocking_response)

    def prepare_properties(self, ctx, config):
        app_id = config.get('app_id').lower()
        vid = ctx.get('vid') if ctx.get('vid') is not None else ''
        uuid = ctx.get('uuid')
        custom_logo = config.get('CUSTOM_LOGO') if config.get('CUSTOM_LOGO') is not None else ''
        is_mobile_num = 1 if ctx.get('is_mobile') else 0
        captcha_uri = 'captcha.js?a={}&u={}&v={}&m={}'.format(ctx.get('block_action'), uuid, vid, is_mobile_num)

        if config.get('first_party') and not ctx.get('is_mobile'):
            prefix = app_id[2:]
            js_client_src = '/{}/{}'.format(prefix, px_constants.CLIENT_FP_PATH)
            captcha_src = '/{}/{}/{}'.format(prefix, px_constants.CAPTCHA_FP_PATH, captcha_uri)
            host_url = '/{}/{}'.format(prefix, px_constants.XHR_FP_PATH)
        else:
            js_client_src = '//{}/{}/main.min.js'.format(px_constants.CLIENT_HOST, app_id)
            captcha_src = '//{}/{}/{}'.format(px_constants.CAPTCHA_HOST, app_id, captcha_uri)
            host_url = px_constants.COLLECTOR_URL.format(app_id.lower())

        return {
            'refId': uuid,
            'appId': app_id,
            'vid': vid,
            'uuid': uuid,
            'customLogo': custom_logo,
            'cssRef': config.get('css_ref'),
            'jsRef': config.get('js_ref'),
            'logoVisibility': 'visible' if custom_logo is not None else 'hidden',
            'hostUrl': host_url,
            'jsClientSrc': js_client_src,
            'firstPartyEnabled': config.get('first_party'),
            'blockScript': captcha_src
        }

    def is_json_response(self, ctx):
        headers = ctx.get('headers')
        if ctx.get('block_action') is not 'r':
            for item in headers.keys():
                if (item.lower() is 'accept' or item.lower() is 'content-type') and headers[item] is 'application/json':
                    return True
        return False
