import re
from time import gmtime, time

import px_constants


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def handle_proxy_headers(filtered_headers, ip, is_gae):
    if 'x-px-gae' in filtered_headers.keys():
        del filtered_headers['x-px-gae']
    for item in filtered_headers.keys():
        if item.upper() == px_constants.FIRST_PARTY_FORWARDED_FOR:
            filtered_headers[item] = ip
        else:
            filtered_headers[px_constants.FIRST_PARTY_FORWARDED_FOR] = ip
    if is_gae:
        filtered_headers["x-px-gae"] = "true"
    return filtered_headers


def is_static_file(ctx):
    uri = ctx.uri
    static_extensions = ['.css', '.bmp', '.tif', '.ttf', '.docx', '.woff2', '.js', '.pict', '.tiff', '.eot',
                         '.xlsx', '.jpg', '.csv', '.eps', '.woff', '.xls', '.jpeg', '.doc', '.ejs', '.otf', '.pptx',
                         '.gif', '.pdf', '.swf', '.svg', '.ps', '.ico', '.pls', '.midi', '.svgz', '.class', '.png',
                         '.ppt', '.mid', 'webp', '.jar']

    for ext in static_extensions:
        if uri.endswith(ext):
            return True
    return False


custom_param_pattern = re.compile('(^(custom_param\d|custom_param10)$)')


def prepare_custom_params(config, dict_to_add):
    custom_params = {
        'custom_param1': '',
        'custom_param2': '',
        'custom_param3': '',
        'custom_param4': '',
        'custom_param5': '',
        'custom_param6': '',
        'custom_param7': '',
        'custom_param8': '',
        'custom_param9': '',
        'custom_param10': ''
    }
    if config.enrich_custom_parameters:
        risk_custom_params = config.enrich_custom_parameters(custom_params)
        if risk_custom_params:
            for param in risk_custom_params:
                if re.match(custom_param_pattern, param) and risk_custom_params[param] is not '':
                    dict_to_add[param] = risk_custom_params[param]


weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

monthname = [None,
             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def getExpiryDate(future=31536000):
    now = time()
    year, month, day, hh, mm, ss, wd, y, z = gmtime(now + future)
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % \
           (weekdayname[wd], day, monthname[month], year, hh, mm, ss)
