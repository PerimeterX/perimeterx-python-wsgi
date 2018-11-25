PREFIX_PX_COOKIE_V1 = '_px'
PREFIX_PX_COOKIE_V3 = '_px3'

TRANS_5C = b"".join(chr(x ^ 0x5C) for x in range(256))
TRANS_36 = b"".join(chr(x ^ 0x36) for x in range(256))

BLOCK_TEMPLATE = 'block_template.mustache'
RATELIMIT_TEMPLATE = 'ratelimit.mustache'
CAPTCHA_ACTION_CAPTCHA = 'c'
BLOCK_ACTION_CAPTCHA = 'b'
BLOCK_ACTION_CHALLENGE = 'j'
BLOCK_ACTION_RATE = 'r'
CLIENT_HOST = 'client.perimeterx.net'
CAPTCHA_HOST = 'captcha.px-cdn.net'
COLLECTOR_URL = 'https://collector-{}.perimeterx.net'
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
