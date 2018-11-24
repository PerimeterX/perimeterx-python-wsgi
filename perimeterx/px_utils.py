import px_constants


def filter_sensitive_headers(headers, config):
    sensitive_keys = config.get('sensitive_headers')
    if not sensitive_keys is not None:
        return {header_name: sensitive_keys[header_name] for header_name in headers if
                header_name not in sensitive_keys}
    else:
        return headers


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def handle_proxy_headers(headers, config, ip):
    filtered_headers = filter_sensitive_headers(headers, config)
    for item in filtered_headers.keys():
        if item.upper() == px_constants.FIRST_PARTY_FORWARDED_FOR:
            filtered_headers[item] = ip
        else:
            filtered_headers[px_constants.FIRST_PARTY_FORWARDED_FOR] = ip
    return filtered_headers
