
def filterSensitiveHeaders(headers, config):

    sensitive_keys = config.get('SENSITIVE_HEADERS')
    if not sensitive_keys == None:
        retval = {}
        for header_name in headers:
            if not header_name in sensitive_keys:
                retval[header_name] = sensitive_keys[header_name]
        return retval
    else:
        return headers

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

