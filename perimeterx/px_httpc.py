import httplib
import json
import time


class PxHttpClient(object):
    def __init__(self, config={}):
        self.config = config
        self.http_client = httplib.HTTPConnection(config.get('perimeterx_server_host'), timeout=config.get('api_timeout', 1))
        self.config['logger'].debug("PxHttpClient init completed")

    def send(self, uri, body, ctx):
        logger = self.config['logger']
        headers = {
            'Authorization': 'Bearer ' + self.config.get('auth_token', ''),
            'Content-Type': 'application/json'
        }
        start = int(round(time.time() * 1000))
        try:

            self.http_client.request('POST', uri, body=json.dumps(body), headers=headers)
            r = self.http_client.getresponse()

            if r.status != 200:
                logger.error('error posting server to server call ' + r.reason)
                return False

            ctx['risk_rtt'] = int(round(time.time() * 1000)) - start
            response_body = r.read()

            return json.loads(response_body)
        except:
            ctx['risk_rtt'] = int(round(time.time() * 1000)) - start
            logger.error('error, could not post request to server, request was not completed')
            raise
