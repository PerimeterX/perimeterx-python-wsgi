![image](http://media.marketwire.com/attachments/201604/34215_PerimeterX_logo.jpg)

[PerimeterX](http://www.perimeterx.com) Python WSGI Middleware
=============================================================
> The PerimeterX Python Middleware is supported by all [WSGI based frameworks](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface#WSGI-compatible_applications_and_frameworks)

Table of Contents
-----------------

-   [Usage](#usage)
  *   [Dependencies](#dependencies)
  *   [Installation](#installation)
  *   [Basic Usage Example](#basic-usage)
-   [Configuration](#configuration)
  *   [Blocking Score](#blocking-score)
  *   [Custom Block Action](#custom-block)
  *   [Enable/Disable Captcha](#captcha-support)
  *   [Extracting Real IP Address](#real-ip)
  *   [Filter Sensitive Headers](#sensitive-headers)
  *   [API Timeouts](#api-timeout)
  *   [Send Page Activities](#send-page-activities)
  *   [Debug Mode](#debug-mode)
-   [Contributing](#contributing)
  *   [Tests](#tests)

<a name="Usage"></a>

<a name="dependencies"></a> Dependencies
----------------------------------------

-  [Python v2.7](https://www.python.org/download/releases/2.7/)
-  [pycrypto v2.6](https://pypi.python.org/pypi/pycrypto)
 - Note: pycrypto is a python core module, this need to be manually added to dependencies when using GAE
 

<a name="installation"></a> Installation
----------------------------------------

Installation can be done using composer

```sh
$ pip install perimeterx
```

### <a name="basic-usage"></a> Basic Usage Example
```python
from perimeterx.middleware import PerimeterX

px_config = {
   'app_id': 'APP_ID',
   'cookie_key': 'COOKIE_KEY',
   'auth_token': 'AUTH_TOKEN',
	'blocking_score': 70
}

application = get_wsgi_application()
application = PerimeterX(application, px_config)
```
### <a name="configuration"></a> Configuration Options

#### Configuring Required Parameters

Configuration options are set in `px_config`

#### Required parameters:

- app_id
- cookie_key
- auth_token

#### <a name="blocking-score"></a> Changing the Minimum Score for Blocking

**default:** 70

```python
px_config = {
	..
    'blocking_score': 75
    ..
}
```

#### <a name="custom-block"></a> Custom Blocking Actions
Setting a custom block handler customizes is done by setting `custom_block_handler` with a user function named on the `px_config`.

Custom handler should contain the action that is taken when a user visits with a high score. Common customizations are to present a reCAPTHA or custom branded block page.

**default:** return HTTP status code 403 and serve the Perimeterx block page.

```python
def custom_block_handler(ctx, start_response):
    start_response('403 Forbidden', [('Content-Type', 'text/html')])
    return ['You have been blocked']


px_config = {
	..
	'custom_block_handler': custom_block_handler,
	..
}

application = get_wsgi_application()
application = PerimeterX(application, px_config)
```      

###### Examples

**Serve a Custom HTML Page**

```python
def custom_block_handler(ctx, start_response):
    block_score = ctx.get('risk_score')
    block_uuid = ctx.get('uuid')
    full_url = ctx.get('full_url')

    html = '<div>Access to ' + full_url + ' has been blocked.</div> ' \
                  '<div>Block reference - ' + uuid + ' </div> ' \
                  '<div>Block score - ' + $block_score + '</div>'

	start_response('403 Forbidden', [('Content-Type', 'text/html')])
	return [html]
};

application = get_wsgi_application()
application = PerimeterX(application, px_config)
```

#### <a name="module-score"></a> Module Mode

**default:** `active_monitoring`

**Possible Values:** - `['active_monitoring', 'active_blocking', 'inactive']`

```python
px_config = {
	..
    'module_mode': 'active_blocking'
    ..
}
```

#### <a name="captcha-support"></a>Enable/disable captcha in the block page

By enabling captcha support, a captcha will be served as part of the block page giving real users the ability to answer, get score clean up and passed to the requested page.

**default: true**

```python
px_config = {
	..
    'captcha_enabled': true
    ..
}
```

#### <a name="real-ip"></a>Extracting the Real User IP Address

In order to evaluate user's score properly, the PerimeterX module
requires the real socket ip (client IP address that created the HTTP
request). The user ip can be returned to the PerimeterX module using a custom user function defined on `px_config`.

**default value:** `environ.get('REMOTE_ADDR')`

```python
def ip_handler(environ):
    for key in environ.keys():
        if key == 'HTTP_X_FORWARDED_FOR':
            xff = environ[key].split(' ')[1]
            return xff
    return '1.2.3.4'
    
px_config = {
	..
   'ip_handler': ip_handler,
	..
}

    
application = get_wsgi_application()
application = PerimeterX(application, px_config)
```

#### <a name="sensitive-headers"></a> Filter sensitive headers

A user can define a list of sensitive header he want to prevent from being send to perimeterx servers (lowered case header name), filtering cookie header for privacy is set by default and will be overridden if a user set the configuration

**default value:** `['cookie', 'cookies']`

```python
px_config = {
	..
    'sensitive_headers': ['cookie', 'cookies', 'secret-header']
	..
}
```

#### <a name="api-timeout"></a>API Timeouts

Control the timeouts for PerimeterX requests. The API is called when the risk cookie does not exist, or is expired or invalid.

API Timeout in seconds (float) to wait for the PerimeterX server API response.


**default:** 1

```python
px_config = {
	..
    'api_timeout': 2
    ..
}
```


#### <a name="send-page-activities"></a> Send Page Activities

Boolean flag to enable or disable sending activities and metrics to
PerimeterX on each page request. Enabling this feature will provide data
that populates the PerimeterX portal with valuable information such as
amount requests blocked and API usage statistics.

**default:** false

```python
px_config = {
	..
    'send_page_activities': true
    ..
}
```

#### <a name="debug-mode"></a> Debug Mode

Enables debug logging

**default:** false

```python
px_config = {
	..
    'debug_mode': true
    ..
}
```
<a name="contributing"></a> Contributing
----------------------------------------
