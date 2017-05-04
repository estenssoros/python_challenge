import logging
import logging.handlers
import os
import sys


class MyLogger(object):
    def __init__(self, prog=None, to_console=True):
        if prog is None:
            prog = os.path.basename(sys.argv[0])
            if prog.endswith('.py'):
                prog = prog[:-3]

        self.my_logger = logging.getLogger(prog)
        if os.path.exists('log'):
            LOG_DIR = 'log'
        else:
            LOG_DIR = None
        if LOG_DIR:
            LOG_FILENAME = os.path.join(LOG_DIR, prog + '.log')
        else:
            LOG_FILENAME = prog + '.log'
        # Set up a specific logger with our desired output level
        self.my_logger.setLevel(logging.DEBUG)

        # Add the log message handler to the logger
        self.log_filename = LOG_FILENAME
        self.handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5 * 1024 * 1024, backupCount=15)
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.handler.setFormatter(self.formatter)
        self.handler.setLevel(logging.DEBUG)
        self.my_logger.addHandler(self.handler)

        if to_console:
            self.consolehandler = logging.StreamHandler()
            self.consolehandler.setLevel(logging.WARN)
            self.consoleformatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            self.consolehandler.setFormatter(self.consoleformatter)
            self.my_logger.addHandler(self.consolehandler)

    def getLogger(self):
        return self.my_logger

    def getConsoleHandler(self):
        return self.consolehandler

    def getHandler(self):
        return self.handler


def mylogger():
    return MyLogger().getLogger()
