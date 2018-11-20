import px_constants
import px_logger
import px_httpc
import px_utils

hoppish = { 'connection', 'keep-alive', 'proxy-authenticate',
    'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
    'upgrade'
}

class PXProxy(object):
    def __init__(self, px_config, pxCtx):
        reverse_app_id = px_config['app_id'][2:]
        self.client_reverse_prefix = '/{}/{}'.format(reverse_app_id, px_constants.CLIENT_FP_PATH)
        self.xhr_reverse_prefix = '/{}/{}'.format(reverse_app_id, px_constants.XHR_PATH)
        self.captcha_reverse_prefix = '/{}/{}'.format(reverse_app_id, px_constants.CAPTCHA_PATH)



    def should_reverse_request(self, uri):
        if uri.startswith(self.client_reverse_prefix) or uri.startswith(self.xhr_reverse_prefix)  or uri.startswith(self.captcha_reverse_prefix):
            return True
        return False


    def handle_reverse_request(self, environ, config, ctx, start_response):
        uri = ctx.get('uri')
        if uri.startswith(self.client_reverse_prefix):
            return self.send_reverse_client_request(config=config, context=ctx, start_response=start_response)
        if uri.startswith(self.xhr_reverse_prefix):
            return self.send_reverse_xhr_request(config=config, context=ctx, start_response=start_response)


    def send_reverse_client_request(self, config, context, start_response):
        if not config['first_party']:
            status = 200
            headers = {
                'Content-Type', 'application/javascript'
            }
            start_response(status, headers)
            return ''

        client_request_uri = '/{}/main.min.js'.format(config['app_id'])
        # px_logger.Logger.debug('Forwarding request from {} to client at {}{}'.format(ctx.get('uri').lower(),pxConfig.CLIENT_HOST,clientRequestUri))
        headers = {'host': config['client_host'],
                   px_constants.FIRST_PARTY_HEADER: 1,
                   px_constants.ENFORCER_TRUE_IP_HEADER: context['ip']}
        filtered_headers = px_utils.filterSensitiveHeaders(context['headers'], config)
        filtered_headers = px_utils.merge_two_dicts(filtered_headers, headers)
        response = px_httpc.sendReverse(url=config['client_host'], path=client_request_uri, body= '', headers=filtered_headers,config=config)
        # headers_dict = dict(response.getheaders())
        headers = filter(lambda x: x[0] not in hoppish, response.getheaders())
        start_response(str(response.status) + ' ' + response.reason, headers)
        return response.read()

    def send_reverse_xhr_request(self, config, context, start_response):
        if None:
            print "asdsadas"
        # if (!pxConfig.FIRST_PARTY_ENABLED | | !pxConfig.FIRST_PARTY_XHR_ENABLED) {
        # if (req.originalUrl.toLowerCase().includes('gif')) {
        # res = {
        # status: 200,
        #         header: {key: 'Content-Type', value: 'image/gif'},
        #                 body: Buffer.
        # from
        # (pxConfig.EMPTY_GIF_B64, 'base64')
        # };
        # } else {
        #     res = {
        #     status: 200,
        #     header: {key: 'Content-Type', value: 'application/json'},
        #     body: {}
        # };
        # }
        # return cb(null, res);
        # }
        # pass


