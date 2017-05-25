import httplib
import px_httpc
import px_constants
import socket


def format_headers(headers):
    ret_val = []
    for key in headers.keys():
        ret_val.append({'name': key, 'value': headers[key]})
    return ret_val


class PxApi(object):

    def __init__(self, config):
        self.config = config
        self.px_http_client = px_httpc.PxHttpClient(self.config)

    def send_risk_request(self, ctx):
        body = self.prepare_risk_body(ctx)
        return self.px_http_client.send(uri='/api/v2/risk', body=body, ctx=ctx)

    def verify(self, ctx):
        logger = self.config['logger']
        logger.debug("PxAPI[verify]")
        try:
            response = self.send_risk_request(ctx)
            if response:
                score = response['score']
                ctx['score'] = score
                ctx['uuid'] = response['uuid']
                ctx['block_action'] = response['action']
                if score >= self.config.get('blocking_score'):
                    logger.debug("PxAPI[verify] block score threshold reached")
                    ctx['block_reason'] = 's2s_high_score'
                else:
                    ctx['pass_reason'] = px_constants.PASS_REASON_S2S
                logger.debug("PxAPI[verify] S2S completed")
                return True
            else:
                return False
        except (httplib.HTTPException, socket.error) as ex:
            # Fail open
            logger.error("PxApi[verify]: s2s timeout posting to server: " + str(ex.message))
            ctx['pass_reason'] = px_constants.PASS_REASON_S2S_TIMEOUT

            return True
        except:
            logger.error('PxApi[verify]: could not complete server to server verification')
            ctx["pass_reason"] = px_constants.PASS_REASON_ERROR
            return True

    def prepare_risk_body(self, ctx):
        logger = self.config['logger']
        logger.debug("PxAPI[send_risk_request]")
        body = {
            'request': {
                'ip': ctx.get('socket_ip'),
                'headers': format_headers(ctx.get('headers')),
                'uri': ctx.get('uri'),
                'url': ctx.get('full_url', '')
            },
            'vid': ctx.get('vid', ''),
            'uuid': ctx.get('uuid', ''),
            'additional': {
                's2s_call_reason': ctx.get('s2s_call_reason', ''),
                'http_method': ctx.get('http_method', ''),
                'http_version': ctx.get('http_version', ''),
                'module_version': self.config.get('module_version', ''),
                'risk_mode': self.config.get('module_mode', ''),
                'px_cookie_hmac': ctx.get('cookie_hmac', '')
            }
        }

        if ctx['s2s_call_reason'] == 'cookie_decryption_failed':
            logger.debug('attaching orig_cookie to request')
            body['additional']['px_cookie_orig'] = ctx.get('px_orig_cookie')

        if ctx['s2s_call_reason'] in ['cookie_expired', 'cookie_validation_failed']:
            logger.debug('attaching px_cookie to request')
            body['additional']['px_cookie'] = ctx.get('decoded_cookie')

        logger.debug("PxAPI[send_risk_request] request body: " + str(body))
        return body
