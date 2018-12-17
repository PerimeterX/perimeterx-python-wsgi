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

        request_time = time.time() - start
        logger.debug('PerimeterX server call took {} ms'.format(request_time))
        return response
    except requests.exceptions.RequestException as err:
        logger.debug('Received RequestException. Error: {}'.format(err))
        raise err
