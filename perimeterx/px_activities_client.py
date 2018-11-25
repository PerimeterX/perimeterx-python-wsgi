import time
import px_httpc
import threading
import traceback, sys
import px_constants

ACTIVITIES_BUFFER = []
CONFIG = {}


def send_activities():
    global ACTIVITIES_BUFFER
    while True:
        if len(ACTIVITIES_BUFFER) > 0:
            chunk = ACTIVITIES_BUFFER[:10]
            ACTIVITIES_BUFFER = ACTIVITIES_BUFFER[10:]
            px_httpc.send(px_constants.API_ACTIVITIES, chunk, CONFIG)
        time.sleep(1)


t1 = threading.Thread(target=send_activities)
t1.daemon = True
t1.start()


def send_to_perimeterx(activity_type, ctx, config, detail):
    global CONFIG
    try:
        if activity_type == 'page_requested' and not config.send_page_activities:
            print 'Page activities disabled in config - skipping.'
            return

        if not CONFIG:
            CONFIG = config

        _details = {
            'http_method': ctx.get('http_method', ''),
            'http_version': ctx.get('http_version', ''),
            'module_version': config.module_version,
            'risk_mode': config.module_mode,
        }

        if len(detail.keys()) > 0:
            _details = dict(_details.items() + detail.items())

        data = {
            'type': activity_type,
            'headers': ctx.get('headers'),
            'timestamp': int(round(time.time() * 1000)),
            'socket_ip': ctx.get('ip'),
            'px_app_id': config.app_id,
            'url': ctx.get('full_url'),
            'details': _details,
            'vid': ctx.get('vid', ''),
            'uuid': ctx.get('uuid', '')
        }
        ACTIVITIES_BUFFER.append(data)
    except:
        print traceback.format_exception(*sys.exc_info())
        return


def send_block_activity(ctx, config):
    send_to_perimeterx(px_constants.BLOCK_ACTIVITY, ctx, config, {
        'block_score': ctx.get('risk_score'),
        'client_uuid': ctx.get('uuid'),
        'block_reason': ctx.get('block_reason'),
        'http_method': ctx.get('http_method'),
        'http_version': ctx.get('http_version'),
        'px_cookie': ctx.get('decoded_cookie'),
        'risk_rtt': ctx.get('risk_rtt'),
        #'cookie_origin':,
        'block_action': ctx.get('block_action',''),
        'module_version': px_constants.MODULE_VERSION,
        'simulated_block': config.monitor_mode is 0,
    })

def send_enforcer_telemetry_activity(ctx, config):
    details = {
        'enforcer_configs': config.get_telemetry_config(),
        'node_name': os.hostname(),
        'os_name': os.platform(),
        'update_reason': updateReason,
        'module_version': config.module_version
    }
    body = {
        'type': px_constants.TELEMETRY_ACTIVITY,
        'timestamp': time.time(),
        'px_app_id': config.app_id,
        'details': details
    }

