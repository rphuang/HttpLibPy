from datetime import datetime
import logging

logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(message)s')
#logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s')

class Log(object):
    """ logging utility class """
    # todo: enhancements
    #  - supports multiple log listeners such as console log, csv log, ...
    #  - log to console with colors (ex: red for error)
    #  - flags per listener to enable/disable individual log severity

    EnableInfo = True
    EnableAction = True
    EnableDebug = False

    # whether to write to logging
    WriteToLogging = True
    # whether to write to console (print)
    WriteToConsole = False

    # IotLogger uses INFO to log custom level/severity
    logger = logging.getLogger('IotLogger')
    logger.setLevel(level=logging.INFO)

    @staticmethod
    def info(msg):
        """ log information message """
        if Log.EnableInfo:
            Log._log('INFO', msg)

    @staticmethod
    def error(msg):
        """ log error message """
        Log.logger.error('ERROR %s' %(msg))

    @staticmethod
    def warning(msg):
        """ log warning message """
        Log.logger.warning('WARNING %s' %(msg))

    @staticmethod
    def action(msg):
        """ log action message """
        if Log.EnableAction:
            Log._log('ACTION', msg)

    @staticmethod
    def debug(msg):
        """ log warning message """
        if Log.EnableDebug:
            Log._log('DEBUG', msg)

    @staticmethod
    def log(severity, msg):
        """ use this to log other severity """
        Log._log(severity, msg)

    @staticmethod
    def _log(severity, msg):
        """ log with time stamp and severity """
        if Log.WriteToConsole:
            print('%s %s %s' %(str(datetime.now()), str(severity), str(msg)))
        if Log.WriteToLogging:
            Log.logger.info('%s %s' %(str(severity), msg))

