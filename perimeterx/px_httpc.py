import time

import requests
from requests_toolbelt.adapters import appengine as requests_toolbelt_appengine

# Monkey patch for using requests in app engine
requests_toolbelt_appengine.monkeypatch()


def send(full_url, body, headers, config, method):
    """
    Returns the appropriate response parameters according to blocking parameters
    :param string full_url:
    :param string body:
    :param dict headers:
    :param PxConfig config:
    :param string method:
    :return response: requests.response type
    """
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
        finish = time.time()
        request_time = finish - start
        logger.debug('PerimeterX server call took {} ms'.format(request_time * 1000))
        return response
    except requests.exceptions.RequestException as err:
        logger.debug('Received RequestException. Error: {}'.format(err))
        raise err
