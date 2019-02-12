import time

import requests
import os

#pylint: disable=import-error
if os.environ.get('SERVER_SOFTWARE','').startswith('Google'):
    import requests_toolbelt.adapters.appengine
    requests_toolbelt.adapters.appengine.monkeypatch()
#pylint: enable=import-error

def send(full_url, body, headers, config, method, raise_error = False):
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
        logger.debug('PerimeterX Received Request Exception. Error: {}'.format(err))
        if raise_error:
            raise err
