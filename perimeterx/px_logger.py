class Logger(object):
    def __init__(self, debug=False):
        self.debug_mode = debug

    def debug(self, message):
        if self.debug_mode:
            print '[PerimeterX DEBUG]: ' + message

    def info(self, message):
        if self.debug_mode:
            print '[PerimeterX INFO]: ' + message

    def error(self, message):
        print '[PerimeterX ERROR]: ' + message
