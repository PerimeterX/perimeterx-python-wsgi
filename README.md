[![Build Status](https://travis-ci.org/PerimeterX/perimeterx-python-wsgi.svg?branch=master)](https://travis-ci.org/PerimeterX/perimeterx-python-wsgi)

![image](https://s.perimeterx.net/logo.png)

[PerimeterX](http://www.perimeterx.com) Python Middleware
=============================================================

> Latest stable version: [v2.0.0](link to package)

Table of Contents
-----------------
- [Installation](#installation)
- [Basic Usage Example](#basicUsage)
- [Advanced Blocking Response](#advancedBlockingResponse)
- [Advanced Configuration Options](#configuration)
    * [Module Enabled](#moduleEnabled)
    * [Module Mode](#moduleMode)
    * [Blocking Score](#blockingScore)
    * [Send Page Activities](#sendPageActivities)
    * [Debug Mode](#debugMode)
    * [Sensitive Routes](#sensitiveRoutes)
    * [Whitelist Routes](#whitelistRoutes)
    * [Sensitive Headers](#sensitiveHeaders)
    * [IP Headers](#ipHeaders)
    * [First Party Enabled](#firstPartyEnabled)
    * [Custom Request Handler](#customRequestHandler)
    * [Additional Activity Handler](#additionalActivityHandler)

## <a name="installation"></a> Installation
PerimeterX python middleware is installed via PIP:
`$ pip install --save perimeterx-python-wsgi`

## <a name="basicUsage"></a> Basic Usage Example
To use PerimeterX middleware on a specific route follow this example:

```python
px_config = {
    'app_id': 'APP_ID',
    'cookie_key': 'COOKIE_KEY',
    'auth_token': 'AUTH_TOKEN',
}

application = get_wsgi_application()
application = PerimeterX(application, px_config)

**Note:** app id, cookie secret and auth token are required fields.


```



For details on how to create a custom Captcha page, refer to the [documentation](https://console.perimeterx.com/docs/server_integration_new.html#custom-captcha-section)

## <a name="configuration"></a>Advanced Configuration Options

In addition to the basic installation configuration [above](#basicUsage), the following configurations options are available:

#### <a name="module_enabled"></a>Module Enabled
A boolean flag to enable/disable the PerimeterX Enforcer.

**Default:** true

```python
config = {
  ...
  module_enabled: False
  ...
}
```

#### <a name="module_mode"></a>Module Mode
Sets the working mode of the Enforcer.

Possible values:

* `active_blocking` - Blocking Mode
* `monitor` - Monitoring Mode

**Default:** `monitor` - Monitor Mode

```python
config = {
  ...
  module_mode: 'active_blocking'
  ...
}
```

#### <a name="blocking_score"></a>Blocking Score
Sets the minimum blocking score of a request.

Possible values:

* Any integer between 0 and 100.

**Default:** 100

```python
config = {
  ...
  blocking_score: 100
  ...
}
```

#### <a name="send_page_activities"></a>Send Page Activities
A boolean flag to enable/disable sending activities and metrics to PerimeterX with each request. <br/>
Enabling this feature allows data to populate the PerimeterX Portal with valuable information, such as the number of requests blocked and additional API usage statistics.

**Default:** true

```python
config = {
  ...
  send_page_activities: True
  ...
}
```


#### <a name="debug_mode"></a>Debug Mode
A boolean flag to enable/disable the debug log messages.

**Default:** False

```python
config = {
  ...
  debug_mode: True
  ...
}
```

#### <a name="sensitive_routes"></a> Sensitive Routes
An array of route prefixes that trigger a server call to PerimeterX servers every time the page is viewed, regardless of viewing history.

**Default:** Empty

```python
const config = {
  ...
  sensitive_routes: ['/login', '/user/checkout']
  ...
}
```

#### <a name="whitelist_routes"></a> Whitelist Routes
An array of route prefixes which will bypass enforcement (will never get scored).

**Default:** Empty

```python
config = {
  ...
  whitelist_routes: ['/about-us', '/careers']
  ...
}
```

#### <a name="sensitive_headers"></a>Sensitive Headers
An array of headers that are not sent to PerimeterX servers on API calls.

**Default:** ['cookie', 'cookies']

```python
config = {
  ...
  sensitive_headers: ['cookie', 'cookies', 'x-sensitive-header']
  ...
}
```

#### <a name="ip_headers"></a>IP Headers
An array of trusted headers that specify an IP to be extracted.

**Default:** Empty

```python
config = {
  ...
  ip_headers: ['x-user-real-ip']
  ...
}
```

#### <a name="first_party_enabled"></a>First Party Enabled
A boolean flag to enable/disable first party mode.

**Default:** True

```python
const pxConfig = {
  ...
  first_party_enabled: False
  ...
}
```

#### <a name="custom_request_handler"></a>Custom Request Handler
A Python function that adds a custom response handler to the request.
Do not forget to declare the function before using it in the config.
Custom request handler is triggered after PerimeterX's verification.
The custom function should handle the response (probably create a new one)
**Default:** Empty

```python
config = {
  ...
  custom_request_handler: custom_request_handler_function,
  ...
}
```

#### <a name="additional_activity_handler"></a>Additional Activity Handler
A Python function that allows interaction with the request data collected by PerimeterX before the data is returned to the PerimeterX servers. Does not alter the response.

**Default:** Empty

```python
config = {
  ...
  additional_activity_handler: additional_activity_handler_function,
  ...
}
```
