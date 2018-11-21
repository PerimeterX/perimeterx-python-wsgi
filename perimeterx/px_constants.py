PREFIX_PX_COOKIE_V1 = '_px'
PREFIX_PX_COOKIE_V3 = '_px3'

TRANS_5C = b"".join(chr(x ^ 0x5C) for x in range(256))
TRANS_36 = b"".join(chr(x ^ 0x36) for x in range(256))

XHR_PATH = 'xhr'
CLIENT_FP_PATH = 'init.js'
CLIENT_TP_PATH = 'main.min.js'
CAPTCHA_PATH = 'captcha'
FIRST_PARTY_HEADER = 'x-px-first-party'
ENFORCER_TRUE_IP_HEADER = 'x-px-enforcer-true-ip'
EMPTY_GIF_B64 = 'R0lGODlhAQABAPAAAAAAAAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
COLLECTOR_URL = 'https://collector-{}.perimeterx.net'
COLLECTOR_HOST = 'collector.perimeterx.net'
FIRST_PARTY_FORWARDED_FOR = 'X-FORWARDED-FOR'
CAPTCHA_HOST = 'captcha.px-cdn.net'
