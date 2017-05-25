import httplib
import socket

from perimeterx import px_constants
from px_httpc import PxHttpClient
import traceback


def format_headers(headers):
    ret_val = []
    for key in headers.keys():
        ret_val.append({'name': key, 'value': headers[key]})
    return ret_val


class PxCaptcha(object):

    def __init__(self, config):
        self.config = config
        self.px_http_client = PxHttpClient(config)

    def send_captcha_request(self, vid, uuid, captcha_value, ctx):
        body = {
            'request': {
                'ip': ctx.get('socket_ip'),
                'headers': format_headers(ctx.get('headers')),
                'uri': ctx.get('uri')
            },
            'pxCaptcha': captcha_value,
            'vid': vid,
            'uuid': uuid,
            'hostname': ctx.get('hostname')
        }
        response = self.px_http_client.send(uri='/api/v1/risk/captcha', body=body, ctx=ctx)

        return response

    def verify(self, ctx, captcha):
        logger = self.config["logger"]
        if not captcha:
            return False

        split_captcha = captcha.split(':')

        if not len(split_captcha) == 3:
            return False

        captcha_value = split_captcha[0]
        vid = split_captcha[1]
        uuid = split_captcha[2]

        if not vid or not captcha_value or not uuid:
            return False

        ctx['uuid'] = uuid
        try:
            response = self.send_captcha_request(vid, uuid, captcha_value, ctx)
            verified = response and response.get('status', 1) == 0
            if verified:
                ctx['pass_reason'] = px_constants.PASS_REASON_CAPTCHA

            return verified
        except  (httplib.HTTPException, socket.error) as ex:
            # Fail open
            logger.error("Error while posting captcha to server in fault of: " + str(ex))
            ctx['pass_reason'] = px_constants.PASS_REASON_CAPTCHA_TIMEOUT
            return True
        except:
            logger.error('could not complete captcha request to server verification')
            ctx['pass_reason'] = px_constants.PASS_REASON_ERROR
            traceback.print_exc()

            return True



