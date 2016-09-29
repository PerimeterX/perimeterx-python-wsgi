import time
import px_httpc
import threading

ACTIVITIES_BUFFER = []
CONFIG = {}


def send_activities():
    global ACTIVITIES_BUFFER
    while True:
        if len(ACTIVITIES_BUFFER) > 0:
            chunk = ACTIVITIES_BUFFER[:10]
            ACTIVITIES_BUFFER = ACTIVITIES_BUFFER[10:]
            px_httpc.send('/api/v1/collector/s2s', chunk, CONFIG)
        time.sleep(1)


t1 = threading.Thread(target=send_activities)
t1.daemon = True
t1.start()


def send_to_perimeterx(activity_type, ctx, config, detail):
    global CONFIG
    if activity_type == 'page_requested' and not config.get('send_page_activities', False):
        return

    if len(CONFIG.keys()) == 0:
        CONFIG = config

    _details = {
        'http_method': ctx.get('http_method', ''),
        'http_version': ctx.get('http_version', ''),
        'module_version': config.get('module_version', ''),
        'risk_mode': config.get('module_mode', '')
    }

    if len(detail.keys()) > 0:
        _details = dict(_details.items() + detail.items())

    data = {
        'type': activity_type,
        'headers': ctx.get('headers'),
        'timestamp': int(round(time.time() * 1000)),
        'socket_ip': ctx.get('socket_ip'),
        'px_app_id': config.get('app_id'),
        'url': ctx.get('full_url'),
        'detail': _details,
        'vid': ctx.get('vid', '')
    }

    ACTIVITIES_BUFFER.append(data)


def send_block_activity(ctx, config):
    send_to_perimeterx('block', ctx, config, {
        'block_score': ctx.get('risk_score'),
        'block_uuid': ctx.get('uuid'),
        'block_reason': ctx.get('block_reason')
    })
