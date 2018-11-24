import px_constants


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def handle_proxy_headers(filtered_headers, ip):
    for item in filtered_headers.keys():
        if item.upper() == px_constants.FIRST_PARTY_FORWARDED_FOR:
            filtered_headers[item] = ip
        else:
            filtered_headers[px_constants.FIRST_PARTY_FORWARDED_FOR] = ip
    return filtered_headers
