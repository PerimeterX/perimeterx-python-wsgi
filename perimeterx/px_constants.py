PREFIX_PX_COOKIE_V1 = '_px'
PREFIX_PX_COOKIE_V3 = '_px3'
PREFIX_PX_TOKEN_V1 = '1'
PREFIX_PX_TOKEN_V3 = '3'
MOBILE_SDK_HEADER = "x-px-authorization"
MOBILE_SDK_ORIGINAL_HEADER= "x-px-original-token"

TRANS_5C = b"".join(chr(x ^ 0x5C) for x in range(256))
TRANS_36 = b"".join(chr(x ^ 0x36) for x in range(256))