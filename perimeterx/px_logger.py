import logging

class Logger(object):
    def __init__(self, debug, app_id):
        self.debug_mode = debug
        self.app_id = app_id

        # Setup logger
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[PerimeterX %(levelname)s][{}]: %(message)s'.format(self.app_id))
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def debug(self, message):
		if self.debug_mode:
			self.logger.debug(message)

    def error(self, message):
        self.logger.error(message)
