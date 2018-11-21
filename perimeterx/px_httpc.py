import httplib
import json
import time

http_client = None


def init(config):
    global http_client
    http_client = httplib.HTTPConnection(config.get('perimeterx_server_host'), timeout=config.get('api_timeout', 1))


def send(uri, body, config):
    logger = config['logger']
    headers = {
        'Authorization': 'Bearer ' + config.get('auth_token', ''),
        'Content-Type': 'application/json'
    }
    try:
        start = time.time()
        http_client.request('POST', uri, body=json.dumps(body), headers=headers)
        r = http_client.getresponse()

        if r.status != 200:
            logger.error('error posting server to server call ' + r.reason)
            return False

        logger.debug('Server call took ' + str(time.time() - start) + 'ms')
        response_body = r.read()

        return json.loads(response_body)
    except httplib.HTTPException:
        init(config)
        return False

def sendReverse(url, path, body, headers, config, method):
    logger = config['logger']
    try:
        start = time.time()
        http_client = httplib.HTTPSConnection(url, timeout=config.get('api_timeout', 1))
        http_client.request(method, path, body, headers=headers)
        response = http_client.getresponse()

        if response.status != 200:
            logger.error('error posting server to server call ' + response.reason)
            return False

        logger.debug('Server call took ' + str(time.time() - start) + 'ms')
        return response

    except httplib.HTTPException:
        init(config)
        return False

