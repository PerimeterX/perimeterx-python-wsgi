import time
import threading
import traceback
import sys
import traceback
from px_httpc import PxHttpClient

ACTIVITIES_BUFFER = []


class PxActivitiesClient(object):

    def __init__(self, config):
        self.config = config
        self.px_http_client = PxHttpClient(config)
        t1 = threading.Thread(target=self.send_activities)
        t1.daemon = True
        t1.start()

    def send_activities(self):
        global ACTIVITIES_BUFFER
        while True:
            if len(ACTIVITIES_BUFFER) > 0:
                chunk = ACTIVITIES_BUFFER[:10]
                ACTIVITIES_BUFFER = ACTIVITIES_BUFFER[10:]
                try:
                    self.px_http_client.send(uri='/api/v1/collector/s2s', body=chunk, ctx={})
                except:
                    traceback.print_exc()
                    self.config["logger"].info("Sending activities to server timed out")
            time.sleep(1)

    def send_to_perimeterx(self, activity_type, ctx, detail):
        try:
            if not self.config.get('server_calls_enabled', True):
                return

            if activity_type == 'page_requested' and not self.config.get('send_page_activities', False):
                self.config["logger"].info("Page activities disabled in config - skipping")
                return

            _details = {
                'http_method': ctx.get('http_method', ''),
                'http_version': ctx.get('http_version', ''),
                'module_version': self.config.get('module_version', ''),
                'risk_mode': self.config.get('module_mode', '')
            }

            if len(detail.keys()) > 0:
                _details = dict(_details.items() + detail.items())

            data = {
                'type': activity_type,
                'headers': ctx.get('headers'),
                'timestamp': int(round(time.time() * 1000)),
                'socket_ip': ctx.get('socket_ip'),
                'px_app_id': self.config.get('app_id'),
                'url': ctx.get('full_url'),
                'details': _details,
                'vid': ctx.get('vid', ''),
                'uuid': ctx.get('uuid', '')
            }
            ACTIVITIES_BUFFER.append(data)
        except:
            print self.config["logger"].error(traceback.format_exception(*sys.exc_info()))
            return

    def send_block_activity(self, ctx):
        self.send_to_perimeterx('block', ctx, {
            'block_score': ctx.get('risk_score'),
            'client_uuid': ctx.get('uuid'),
            'block_reason': ctx.get('block_reason')
        })
