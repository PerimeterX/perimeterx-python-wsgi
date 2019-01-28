import base64

from werkzeug.wrappers import Response

import px_constants
import px_httpc
import px_utils
import os

hoppish = {'connection', 'keep-alive', 'proxy-authenticate',
           'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
           'upgrade'
           }


def delete_extra_headers(filtered_headers):
    if 'content-length' in filtered_headers.keys():
        del filtered_headers['content-length']
    if 'content-type' in filtered_headers.keys():
        del filtered_headers['content-type']


class PxProxy(object):
    def __init__(self, config):
        self._logger = config.logger
        self.is_gae = os.environ.get('SERVER_SOFTWARE','').startswith('Google')
        reverse_app_id = config.app_id[2:]
        self.client_reverse_prefix = '/{}/{}'.format(reverse_app_id, px_constants.CLIENT_FP_PATH).lower()
        self.xhr_reverse_prefix = '/{}/{}'.format(reverse_app_id, px_constants.XHR_FP_PATH).lower()
        self.captcha_reverse_prefix = '/{}/{}'.format(reverse_app_id, px_constants.CAPTCHA_FP_PATH).lower()

    def should_reverse_request(self, uri):
        uri = uri.lower()
        if uri.startswith(self.client_reverse_prefix) or uri.startswith(self.xhr_reverse_prefix) or uri.startswith(
                self.captcha_reverse_prefix):
            return True
        return False

    def handle_reverse_request(self, config, ctx, body):
        uri = ctx.uri.lower()

        if uri.startswith(self.client_reverse_prefix):
            status, headers, data = self.send_reverse_client_request(config=config, ctx=ctx)
        elif uri.startswith(self.xhr_reverse_prefix):
            status, headers, data = self.send_reverse_xhr_request(config=config, ctx=ctx, body=body)
        elif uri.startswith(self.captcha_reverse_prefix):
            status, headers, data = self.send_reverse_captcha_request(config=config, ctx=ctx)
        px_response = Response(data)
        px_response.headers = filter_hop_by_hop_headers(headers)
        px_response.status = status
        return px_response

    def send_reverse_client_request(self, config, ctx):
        if not config.first_party:
            headers = {'Content-Type': 'application/javascript'}
            return '200 OK', headers, ''

        client_request_uri = '/{}/main.min.js'.format(config.app_id)
        msg = 'Forwarding request from {} to client at {}{}'
        self._logger.debug(msg.format(ctx.uri.lower(), px_constants.CLIENT_HOST, client_request_uri))

        headers = {'host': px_constants.CLIENT_HOST,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: ctx.ip}
        filtered_headers = px_utils.handle_proxy_headers(ctx.headers, ctx.ip, self.is_gae)
        filtered_headers = px_utils.merge_two_dicts(filtered_headers, headers)
        delete_extra_headers(filtered_headers)
        px_response = px_httpc.send(full_url=px_constants.CLIENT_HOST + client_request_uri, body='',
                                    headers=filtered_headers, config=config, method='GET')
        if self.is_gae:
            data = px_response.raw.read(decode_content=True)
        else:
            data = px_response.raw.read()
        headers = px_response.headers
        status = str(px_response.status_code) + ' ' + str(px_response.reason)
        return status, headers, data

    def send_reverse_xhr_request(self, config, ctx, body):
        uri = ctx.uri
        if not config.first_party or not config.first_party_xhr_enabled:
            body, response_headers = self.return_default_response(uri)
            return '200 OK', response_headers, body

        xhr_path_index = uri.find('/' + px_constants.XHR_FP_PATH)
        suffix_uri = uri[xhr_path_index + 4:]
        host = config.collector_host
        headers = {'host': host,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: ctx.ip}

        if ctx.vid is not None:
            headers['cookie'] = 'pxvid=' + ctx.vid

        filtered_headers = px_utils.handle_proxy_headers(ctx.headers, ctx.ip, self.is_gae)
        filtered_headers = px_utils.merge_two_dicts(filtered_headers, headers)
        msg = 'Forwarding request from {} to client at {}{}'
        self._logger.debug(msg.format(ctx.uri.lower(), host, suffix_uri))
        px_response = px_httpc.send(full_url=host + suffix_uri + "?" + ctx.query_params, body=body,
                                    headers=filtered_headers, config=config, method=ctx.http_method)

        if px_response.status_code >= 400:
            data, response_headers = self.return_default_response(uri)
            self._logger.debug('Error reversing the http call: {}'.format(px_response.reason))
            return '200 OK', response_headers, data
        data = px_response.content
        headers = px_response.headers
        status = str(px_response.status_code) + ' ' + str(px_response.reason)
        return status, headers, data

    def send_reverse_captcha_request(self, config, ctx):
        if not config.first_party:
            status = '200 OK'
            response_headers = {'Content-Type': 'application/javascript'}
            return status, response_headers, ''
        uri = '/{}{}?{}'.format(config.app_id, ctx.uri.lower().replace(self.captcha_reverse_prefix, ''),
                                ctx.query_params)
        host = px_constants.CAPTCHA_HOST

        headers = {'host': px_constants.CAPTCHA_HOST,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: ctx.ip}
        filtered_headers = px_utils.handle_proxy_headers(ctx.headers, ctx.ip, self.is_gae)
        filtered_headers = px_utils.merge_two_dicts(filtered_headers, headers)
        delete_extra_headers(filtered_headers)
        self._logger.debug('Forwarding request from {} to client at {}{}'.format(ctx.uri.lower(), host, uri))
        px_response = px_httpc.send(full_url=host + uri, body='',
                                    headers=filtered_headers, config=config, method='GET')
        if self.is_gae:
            data = px_response.raw.read(decode_content=True)
        else:
            data = px_response.raw.read()
        headers = px_response.headers
        status = str(px_response.status_code) + ' ' + str(px_response.reason)
        return status, headers, data

    def return_default_response(self, uri):
        if 'gif' in uri.lower():
            headers = {'Content-Type': 'image/gif'}
            body = base64.b64decode(px_constants.EMPTY_GIF_B64)
        else:
            headers = {'Content-Type': 'application/json'}
            body = {}
        return body, headers

def filter_hop_by_hop_headers(response_headers):
    headers = {}
    for key in response_headers.keys():
        if key.lower() not in hoppish:
            headers[key] = response_headers[key]
    return headers