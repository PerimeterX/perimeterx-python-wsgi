import json
import socket
import sys
import threading
import time
import traceback

import px_constants
import px_httpc
import px_utils

ACTIVITIES_BUFFER = []
CONFIG = {}


def init_activities_configuration(config):
    global CONFIG
    CONFIG = config

def _send_activities_chunk():
    global ACTIVITIES_BUFFER
    default_headers = {
        'Authorization': 'Bearer ' + CONFIG.auth_token,
        'Content-Type': 'application/json'
    }
    full_url = CONFIG.server_host + px_constants.API_ACTIVITIES
    chunk = ACTIVITIES_BUFFER[:10]
    for _ in range(len(chunk)):
        ACTIVITIES_BUFFER.pop(0)
    px_httpc.send(full_url=full_url, body=json.dumps(chunk), headers=default_headers, config=CONFIG, method='POST')

def send_activities_in_thread():
    if len(ACTIVITIES_BUFFER) >= 10:
        CONFIG.logger.debug('Posting {} Activities'.format(len(ACTIVITIES_BUFFER)))
        t1 = threading.Thread(target=_send_activities_chunk)
        t1.daemon = True
        t1.start()
    else:
        CONFIG.logger.debug('NOT Posting {} Activities: '.format(len(ACTIVITIES_BUFFER)))

def send_to_perimeterx(activity_type, ctx, config, detail):
    try:
        if activity_type == 'page_requested' and not config.send_page_activities:
            print 'Page activities disabled in config - skipping.'
            return
        _details = {
            'http_method': ctx.http_method,
            'http_version': ctx.http_version,
            'module_version': config.module_version,
            'risk_mode': config.module_mode,
        }

        if len(detail.keys()) > 0:
            _details = dict(_details.items() + detail.items())

        data = {
            'type': activity_type,
            'headers': dict(ctx.headers),
            'timestamp': int(round(time.time() * 1000)),
            'socket_ip': ctx.ip,
            'px_app_id': config.app_id,
            'url': ctx.full_url,
            'details': _details,
            'vid': ctx.vid,
            'uuid': ctx.uuid
        }
        if activity_type == 'page_requested' or activity_type == 'block':
            px_utils.prepare_custom_params(config, _details)
            data['pxhd'] = ctx.pxhd

        ACTIVITIES_BUFFER.append(data)
    except:
        print traceback.format_exception(*sys.exc_info())
        return


def send_block_activity(ctx, config):
    send_to_perimeterx(px_constants.BLOCK_ACTIVITY, ctx, config, {
        'block_score': ctx.score,
        'block_uuid': ctx.uuid,
        'block_reason': ctx.block_reason,
        'http_version': ctx.http_version,
        'px_cookie': ctx.decoded_cookie,
        'risk_rtt': ctx.risk_rtt,
        'cookie_origin': ctx.cookie_origin,
        'block_action': ctx.block_action,
        'simulated_block': config.module_mode is px_constants.MODULE_MODE_MONITORING,
    })


def send_page_requested_activity(ctx, config):
    details = {
        'client_uuid': ctx.uuid,
        'pass_reason': ctx.pass_reason,
        'risk_rtt': ctx.risk_rtt
    }

    if ctx.decoded_cookie:
        details['px_cookie'] = ctx.decoded_cookie
    send_to_perimeterx(px_constants.PAGE_REQUESTED_ACTIVITY, ctx, config, details)


def send_enforcer_telemetry_activity(config, update_reason):
    details = {
        'enforcer_configs': config.telemetry_config,
        'node_name': socket.gethostname(),
        'os_name': sys.platform,
        'update_reason': update_reason,
        'module_version': config.module_version
    }
    body = {
        'type': px_constants.TELEMETRY_ACTIVITY,
        'timestamp': time.time(),
        'px_app_id': config.app_id,
        'details': details
    }
    headers = {
        'Authorization': 'Bearer ' + config.auth_token,
        'Content-Type': 'application/json'
    }
    config.logger.debug('Sending telemetry activity to PerimeterX servers')
    px_httpc.send(full_url=config.server_host + px_constants.API_ENFORCER_TELEMETRY, body=json.dumps(body),
                  headers=headers, config=config, method='POST')
