[![Build Status](https://travis-ci.org/PerimeterX/perimeterx-python-wsgi.svg?branch=master)](https://travis-ci.org/PerimeterX/perimeterx-python-wsgi)

![image](https://s.perimeterx.net/logo.png)

[PerimeterX](http://www.perimeterx.com) Python Middleware
=============================================================
> Latest stable version: [v3.1.0](https://pypi.org/project/perimeterx-python-wsgi/)

> Latest GAE stable version: [v3.1.0](https://pypi.org/project/perimeterx-python-wsgi-gae/)

Table of Contents
-----------------
- [Installation](#installation)
- [Upgrading](#upgrading)
- [Required Configuration](#required_config)
- [Advanced Blocking Response](#advanced_blocking_response)
- [Optional Configuration](#configuration)
    * [Module Enabled](#module_enabled)
    * [Module Mode](#module_mode)
    * [Blocking Score](#blocking_score)
    * [Send Page Activities](#send_page_activities)
    * [Debug Mode](#debug_mode)
    * [Sensitive Routes](#sensitive_routes)
    * [Whitelist Routes](#whitelist_routes)
    * [Sensitive Headers](#sensitive_headers)
    * [IP Headers](#ip_headers)
    * [First-Party Enabled](#first_party_enabled)
    * [Custom Request Handler](#custom_request_handler)
    * [Additional Activity Handler](#additional_activity_handler)
    * [Px Disable Request](#px_disable_request)
    * [Test Block Flow on Monitoring Mode](#bypass_monitor_header)

## <a name="installation"></a> Installation

### Standalone

* To install the PerimeterX Python middleware in standalone mode, use PIP as follows:

```python
pip install perimeterx-python-wsgi
```

### Google App Engine

> The following procedure is based on [Google's Third-Party Libraries Guideline](https://cloud.google.com/appengine/docs/standard/python/tools/using-libraries-python-27#installing_a_library)

1. Create a folder to store the PerimeterX Python middleware:
```bash
mkdir lib
```

2. Using PIP, intall the PerimeterX Python middleware with the `-t` flag to have it installed to the folder previouesly created:

```python
pip install -t lib/ perimeterx-python-wsgi-gae
```

3. Create a file named `appengine_config.py` in the same folder as your `app.yaml` file with the following content:
```python
from google.appengine.ext import vendor

vendor.add('lib')
```

4. In your `app.yaml` file, request the following libraries:
```python
libraries:
- name: flask
  version: "0.12"
- name: pycrypto
  version: "2.6.1"
- name: werkzeug
  version: "0.11.10"
- name: ssl
  version: "2.7.11"
```

5. Deploy the app

## <a name="upgrading"></a> Upgrading
To upgrade to the latest PerimeterX Enforcer version, run:

* Standalone: `pip install -U perimeterx-python-wsgi`
* Google App Engine: `pip install -t lib/ -U perimeterx-python-wsgi-gae`

For more information, contact [PerimeterX Support](support@perimeterx.com).

## <a name="required_config"></a> Required Configurations
To use PerimeterX middleware on a specific route follow this example:

```python
from perimeterx.middleware import PerimeterX

px_config = {
    'app_id': 'APP_ID',
    'cookie_key': 'COOKIE_KEY',
    'auth_token': 'AUTH_TOKEN',
}
application = get_wsgi_application()
application = PerimeterX(application, px_config)
```
- The PerimeterX **Application ID** / **AppId** and PerimeterX **Token** / **Auth Token** can be found in the Portal, in [Applications](https://console.perimeterx.com/#/app/applicationsmgmt).
- PerimeterX **Risk Cookie** / **Cookie Key** can be found in the portal, in [Policies](https://console.perimeterx.com/#/app/policiesmgmt).
The Policy from where the **Risk Cookie** / **Cookie Key** is taken must correspond with the Application from where the **Application ID** / **AppId** and PerimeterX **Token** / **Auth Token**.
For details on how to create a custom Captcha page, refer to the [documentation](https://console.perimeterx.com/docs/server_integration_new.html#custom-captcha-section)
## <a name="configuration"></a>Optional Configuration
In addition to the basic installation configuration [above](#required_config), the following configurations options are available:
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
Enable/disable sending activities and metrics to PerimeterX with each request. <br/>
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
Enable/disable the debug log messages.
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
config = {
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
#### <a name="first_party_enabled"></a>First-Party Enabled
Enable/disable First-Party mode.
**Default:** True
```python
config = {
  ...
  first_party: False
  ...
}
```
#### <a name="custom_request_handler"></a>Custom Request Handler
A Python function that adds a custom response handler to the request.</br>
You must declare the function before using it in the config.</br>
The Custom Request Handler is triggered after PerimeterX's verification.
The custom function should handle the response (most likely it will create a new response)
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

#### <a name="pxde"></a>PerimeterX Data Enrichment
This is a cookie we make available for our costumers, that can provide extra data about the request
```python
context.pxde
context.pxde_verified

```

#### <a name="px_disable_request"></a>Px Disable Request
This is a property that allows the developer to disable the module for a single request. Its value should be True for disabling, and False for enabling
```python


...
environ['px_disable_request'] = False #The request shall be passed to the enforcer.
or
environ['px_disable_request'] = True #The enforcer shall be disabled for that request.

```

#### <a name=“bypassMonitorHeader”></a> Test Block Flow on Monitoring Mode

Allows you to test an enforcer’s blocking flow while you are still in Monitor Mode.

When the header name is set(eg. `x-px-block`) and the value is set to `1`, when there is a block response (for example from using a User-Agent header with the value of `PhantomJS/1.0`) the Monitor Mode is bypassed and full block mode is applied. If one of the conditions is missing you will stay in Monitor Mode. This is done per request.
To stay in Monitor Mode, set the header value to `0`.

The Header Name is configurable using the `bypass_monitor_header` property.

**Default:** Empty

```python
config = {
  ...
  bypass_monitor_header: 'x-px-block',
  ...
}
```
