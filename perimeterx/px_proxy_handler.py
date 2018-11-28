import px_constants
import px_logger
import px_httpc
import px_utils
import base64

hoppish = {'connection', 'keep-alive', 'proxy-authenticate',
           'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
           'upgrade'
           }


class PXProxy(object):
    def __init__(self, config):
        self._logger = config.logger

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

    def handle_reverse_request(self, config, ctx, start_response, environ):
        uri = ctx.get('uri').lower()

        if uri.startswith(self.client_reverse_prefix):
            return self.send_reverse_client_request(config=config, context=ctx, start_response=start_response)
        if uri.startswith(self.xhr_reverse_prefix):
            return self.send_reverse_xhr_request(config=config, context=ctx, start_response=start_response, body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', '0'))))
        if uri.startswith(self.captcha_reverse_prefix):
            return self.send_reverse_captcha_request(config=config, context=ctx, start_response=start_response)

    def send_reverse_client_request(self, config, context, start_response):
        if not config.first_party:
            headers = [('Content-Type', 'application/javascript')]
            start_response("200 OK", headers)
            return ""

        client_request_uri = '/{}/main.min.js'.format(config.app_id)
        self._logger.debug('Forwarding request from {} to client at {}{}'.format(context.get('uri').lower(),px_constants.CLIENT_HOST, client_request_uri))

        headers = {'host': px_constants.CLIENT_HOST,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: context.get('ip')}
        filtered_headers = px_utils.handle_proxy_headers(context.get('headers'), context.get('ip'))
        filtered_headers = px_utils.merge_two_dicts(filtered_headers, headers)
        response = px_httpc.send(full_url=px_constants.CLIENT_HOST + client_request_uri, body='',
                                 headers=filtered_headers, config=config, method='GET')

        self.handle_proxy_response(response, start_response)
        return response.content

    def send_reverse_xhr_request(self, config, context, start_response, body):
        uri = context.get('uri')
        if not config.first_party or not config.first_party_xhr_enabled:
            body, content_type = self.return_default_response(uri)

            start_response('200 OK', [content_type])
            return body

        xhr_path_index = uri.find('/' + px_constants.XHR_FP_PATH)
        suffix_uri = uri[xhr_path_index + 4:]

        host = config.collector_host
        headers = {'host': host,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: context.get('ip')}

        if context.get('vid') is not None:
            headers['Cookies'] = '_pxvid=' + context.get('vid')

        filtered_headers = px_utils.handle_proxy_headers(context.get('headers'), context.get('ip'))
        filtered_headers = px_utils.merge_two_dicts(filtered_headers, headers)
        self._logger.debug('Forwarding request from {} to client at {}{}'.format(context.get('uri').lower(), host, suffix_uri))
        response = px_httpc.send(full_url=host + suffix_uri, body=body,
                                 headers=filtered_headers, config=config, method=context.get('http_method'))

        if response.status_code >= 400:
            body, content_type = self.return_default_response(uri)
            px_logger.Logger.debug('error reversing the http call ' + response.reason)
            start_response('200 OK', [content_type])
            return body
        self.handle_proxy_response(response, start_response)
        return response.content

    def handle_proxy_response(self, response, start_response):
        headers = []
        for header in response.headers:
            if header.lower() not in hoppish:
                headers.append((header, response.headers[header]))
        start_response(str(response.status_code) + ' ' + response.reason, headers)

    def return_default_response(self, uri):
        if 'gif' in uri.lower():
            content_type = tuple('Content-Type', 'image/gif')
            body = base64.b64decode(px_constants.EMPTY_GIF_B64)
        else:
            content_type = tuple('Content-Type', 'application/json')
            body = {}
        return body, content_type

    def send_reverse_captcha_request(self, config, context, start_response):
        if not config.first_party:
            status = '200 OK'
            headers = [('Content-Type', 'application/javascript')]
            start_response(status, headers)
            return ''
        uri = '/{}{}?{}'.format(config.app_id, context.get('uri').lower().replace(self.captcha_reverse_prefix, ''), context['query_params'])
        host = px_constants.CAPTCHA_HOST

        headers = {'host': px_constants.CAPTCHA_HOST,
                   px_constants.FIRST_PARTY_HEADER: '1',
                   px_constants.ENFORCER_TRUE_IP_HEADER: context.get('ip')}
        filtered_headers = px_utils.handle_proxy_headers(context.get('headers'), context.get('ip'))
        filtered_headers = px_utils.merge_two_dicts(filtered_headers, headers)
        self._logger.debug('Forwarding request from {} to client at {}{}'.format(context.get('uri').lower(), host, uri))
        response = px_httpc.send(full_url=host + uri, body='',
                                 headers=filtered_headers, config=config, method='GET')
        self.handle_proxy_response(response, start_response)
        return response.content



