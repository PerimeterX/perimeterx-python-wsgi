![image](http://media.marketwire.com/attachments/201604/34215_PerimeterX_logo.jpg)

[PerimeterX](http://www.perimeterx.com) Python WSGI Middleware
=============================================================
> The PerimeterX Python Middleware is supported by all [WSGI based frameworks](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface#WSGI-compatible_applications_and_frameworks).

Table of Contents
-----------------

-   [Usage](#usage)
  *   [Dependencies](#dependencies)
  *   [Installation](#installation)
  *   [Basic Usage Example](#basic-usage)
-   [Configuration](#configuration)
  *   [Blocking Score](#blocking-score)
  *   [Custom Block Action](#custom-block)
  *   [Enable/Disable Server Calls](#server-calls)
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

Installation can be done using Composer.

```sh
$ pip install perimeterx-python-wsgi
```

### <a name="basic-usage"></a> Basic Usage Example
##### Django:

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
##### Google App Engine:
app.yaml:

```yaml
libraries:
- name: pycrypto
  version: 2.6
```

```python
import webapp2
from perimeterx.middleware import PerimeterX

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

px_config = {
   'app_id': 'APP_ID',
   'cookie_key': 'COOKIE_KEY',
   'auth_token': 'AUTH_TOKEN',
	'blocking_score': 70
}

app = PerimeterX(app, px_config)
```

### <a name="configuration"></a> Configuration Options

#### Configuring Required Parameters

Configuration options are set in `px_config`.

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
Setting a custom block handler is done by setting `custom_block_handler` with a user function named on the `px_config`.

The custom handler should contain the action that is taken when a user visits with a high score. Common customizations are to present a reCAPTHA or a custom branded Block Page.

**default:** return HTTP status code 403 and serve the PerimeterX block page.

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
                  '<div>Block score - ' + block_score + '</div>'

	start_response('403 Forbidden', [('Content-Type', 'text/html')])
	return [html]
};

px_config = {
	..
	'custom_block_handler': custom_block_handler,
	..
}

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

#### <a name="server-calls"></a> Enable/Disable Server Calls
 
By disabling server calls, the module will only evaluate users by their cookie. Users without a cookie will not generate a request to the PerimeterX servers.

**default:** `True`

```python
px_config = {
	..
    'server_calls_enabled': False
    ..
}
```

#### <a name="captcha-support"></a>Enable/Disable CAPTCHA on the block page

By enabling CAPTCHA support, a CAPTCHA will be served as part of the block page, giving real users the ability to answer, get their score cleaned up and navigate to the requested page.

**default: True**

```python
px_config = {
	..
    'captcha_enabled': True
    ..
}
```

#### <a name="real-ip"></a>Extracting the Real User IP Address

> Note: IP extraction, according to your network setup, is important. It is common to have a load balancer/proxy on top of your applications, in this case the PerimeterX module will send an internal IP as the user's. In order to perform processing and detection for server-to-server calls, PerimeterX's module requires the real user's IP.

The user's IP can be returned to the PerimeterX module, using a custom user defined function on the `px_config` variable.

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

A user can define a list of sensitive headers that will be excluded from any message sent to PerimeterX's servers (lowere case header names). Filtering the 'cookie' header is set by default (for privacy) and will be overridden if a user specifies otherwise in the configuration.

**default value:** `['cookie', 'cookies']`

```python
px_config = {
	..
    'sensitive_headers': ['cookie', 'cookies', 'secret-header']
	..
}
```

#### <a name="api-timeout"></a>API Timeouts

Controls the timeouts for PerimeterX requests. The API is called when the risk cookie does not exist, is expired or is invalid.

API Timeout in seconds (float) to wait for the PerimeterX servers' API response.


**default:** 1

```python
px_config = {
	..
    'api_timeout': 2
    ..
}
```


#### <a name="send-page-activities"></a> Send Page Activities

A boolean flag to enable or disable sending activities and metrics to
PerimeterX on each page request. Enabling this feature will provide data
that populates the PerimeterX portal with valuable information such as
amount requests blocked and API usage statistics.

A boolean flag to determine whether or not to send activities and metrics to
PerimeterX, on each page request. Enabling this feature will provide PerimeterX with data
that populates the PerimeterX portal, containing valuable information such as
the amount of requests blocked and other API usage statistics.

**default:** false

```python
px_config = {
	..
    'send_page_activities': True
    ..
}
```

#### <a name="debug-mode"></a> Debug Mode

Enables debug logging.

**default:** false

```python
px_config = {
	..
    'debug_mode': True
    ..
}
```
<a name="contributing"></a> Contributing
----------------------------------------
