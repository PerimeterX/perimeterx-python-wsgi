class Logger(object):
    def __init__(self, debug, app_id):
        self.debug_mode = debug
        self.app_id = app_id

    def debug(self, message):
        if self.debug_mode:
            print '[PerimeterX DEBUG][{}]: '.format(self.app_id) + message

    def error(self, message):
        print '[PerimeterX ERROR][{}]: '.format(self.app_id) + message
