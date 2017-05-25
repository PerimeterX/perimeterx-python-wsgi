PREFIX_PX_COOKIE_V1 = '_px'
PREFIX_PX_COOKIE_V3 = '_px3'

TRANS_5C = b"".join(chr(x ^ 0x5C) for x in range(256))
TRANS_36 = b"".join(chr(x ^ 0x36) for x in range(256))

# Pass Reasons
PASS_REASON_NONE = None
PASS_REASON_COOKIE = "cookie"
PASS_REASON_S2S = "s2s"
PASS_REASON_S2S_TIMEOUT = "s2s_timeout"
PASS_REASON_CAPTCHA = "captcha"
PASS_REASON_CAPTCHA_TIMEOUT = "captcha_timeout"
PASS_REASON_ERROR = "error"
