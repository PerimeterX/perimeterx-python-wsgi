import pystache
import px_template
import px_constants
import json
import base64


class PXBlocker(object):
    def __init__(self):
        self.mustache_renderer = pystache.Renderer()
        self.ratelimit_rendered_page = self.mustache_renderer.render(
            px_template.get_template(px_constants.RATELIMIT_TEMPLATE), {})

    def handle_blocking(self, ctx, config):
        action = ctx.block_action
        status = '403 Forbidden'

        is_json_response = self.is_json_response(ctx)
        if is_json_response:
            content_type = 'application/json'
        else:
            content_type = 'text/html'
        headers = [('Content-Type', content_type)]

        if action is px_constants.ACTION_CHALLENGE:
            blocking_props = ctx.block_action_data
            blocking_response = blocking_props
        elif action is px_constants.ACTION_RATELIMIT:
            blocking_response = self.ratelimit_rendered_page
            status = '429 Too Many Requests'
        else:
            blocking_props = self.prepare_properties(ctx, config)
            blocking_response = self.mustache_renderer.render(px_template.get_template(px_constants.BLOCK_TEMPLATE),
                                                              blocking_props)

        if ctx.is_mobile:
            page_response = json.dumps({
                'action': parse_action(ctx.block_action),
                'uuid': ctx.uuid,
                'vid': ctx.vid,
                'appId': config.app_id,
                'page': base64.b64encode(blocking_response),
                'collectorURL': 'https://' + config.collector_host
            })
            return page_response, headers, status

        if is_json_response:
            blocking_response = json.dumps(blocking_props)

        blocking_response = str(blocking_response)
        return blocking_response, headers, status

    def prepare_properties(self, ctx, config):
        app_id = config.app_id
        vid = ctx.vid
        uuid = ctx.uuid
        custom_logo = config.custom_logo
        is_mobile_num = 1 if ctx.is_mobile else 0
        captcha_uri = 'captcha.js?a={}&u={}&v={}&m={}'.format(ctx.block_action, uuid, vid, is_mobile_num)

        if config.first_party and not ctx.is_mobile:
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
            'cssRef': config.css_ref,
            'jsRef': config.js_ref,
            'logoVisibility': 'visible' if custom_logo is not None else 'hidden',
            'hostUrl': host_url,
            'jsClientSrc': js_client_src,
            'firstPartyEnabled': 'true' if config.first_party else 'false',
            'blockScript': captcha_src
        }

    def is_json_response(self, ctx):
        headers = ctx.headers
        if ctx.block_action is not px_constants.ACTION_RATELIMIT:
            for item in headers.keys():
                if item.lower() == 'accept' or item.lower() == 'content-type':
                    item_arr = headers[item].split(',')
                    for header_item in item_arr:
                        if header_item.strip() == 'application/json':
                            return True
        return False


def parse_action(action):
    if 'b' == action:
        return 'block'
    elif 'j' == action:
        return 'challege'
    elif 'r' == action:
        return 'ratelimit'
    else:
        return 'captcha'
