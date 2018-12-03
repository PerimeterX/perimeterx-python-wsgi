import time
import requests


def send(full_url, body, headers, config, method):
    logger = config.logger
    try:
        start = time.time()
        if method == 'GET':
            response = requests.get(url='https://' + full_url, headers=headers, timeout=config.api_timeout, stream=True)
        else:
            response = requests.post(url='https://' + full_url, headers=headers, data=body, timeout=config.api_timeout)

        if response.status_code >= 400:
            logger.debug('PerimeterX server call failed')
            return False

        logger.debug('PerimeterX server call took ' + str(time.time() - start) + 'ms')
        return response
    except requests.exceptions.RequestException as e:
        logger.debug('Received RequestException, message: ' + e.message)
        return False
