PREFIX_PX_COOKIE_V1 = '_px'
PREFIX_PX_COOKIE_V3 = '_px3'
PREFIX_PX_TOKEN_V1 = '1'
PREFIX_PX_TOKEN_V3 = '3'
PREFIX_PX_DATA_ENRICHMENT = '_pxde'
PREFIX_PXVID = '_pxvid'
MOBILE_SDK_HEADER = "x-px-authorization"
MOBILE_SDK_ORIGINAL_HEADER = "x-px-original-token"
MOBILE_SDK_CONNECTION_ERROR_CODE = '2'
MOBILE_SDK_PINNING_ERROR_CODE = '3'

TRANS_5C = b"".join(chr(x ^ 0x5C) for x in range(256))
TRANS_36 = b"".join(chr(x ^ 0x36) for x in range(256))

BLOCK_TEMPLATE = 'block_template.mustache'
RATELIMIT_TEMPLATE = 'ratelimit.mustache'
CLIENT_HOST = 'client.perimeterx.net'
CAPTCHA_HOST = 'captcha.px-cdn.net'
COLLECTOR_URL = 'collector-{}.perimeterx.net'
SERVER_URL = 'sapi-{}.perimeterx.net'
CLIENT_FP_PATH = 'init.js'
CAPTCHA_FP_PATH = 'captcha'
XHR_FP_PATH = 'xhr'
MODULE_MODE_BLOCKING = 'active_blocking'
MODULE_MODE_MONITORING = 'monitor'
CLIENT_TP_PATH = 'main.min.js'
FIRST_PARTY_HEADER = 'x-px-first-party'
ENFORCER_TRUE_IP_HEADER = 'x-px-enforcer-true-ip'
EMPTY_GIF_B64 = 'R0lGODlhAQABAPAAAAAAAAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
COLLECTOR_HOST = 'collector.perimeterx.net'
FIRST_PARTY_FORWARDED_FOR = 'X-FORWARDED-FOR'
MODULE_VERSION = 'Python WSGI Module v2.0.0'
API_RISK = '/api/v3/risk'
PAGE_REQUESTED_ACTIVITY = 'page_requested'
BLOCK_ACTIVITY = 'block'
API_ENFORCER_TELEMETRY = '/api/v2/risk/telemetry'
API_ACTIVITIES = '/api/v1/collector/s2s'
TELEMETRY_ACTIVITY = 'enforcer_telemetry'
ACTION_CHALLENGE = 'j'
ACTION_BLOCK = 'b'
ACTION_RATELIMIT = 'r'
ACTION_CAPTCHA = 'c'
