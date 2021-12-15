from time import sleep
from IotLib.log import Log

def okToSendCommand(peripheral, timeout=0.2):
    """ spin a few cycles wait till the hub is ready to send the command request """
    sleepTime = 0.05
    count = int(timeout / sleepTime)
    while peripheral.hub._sync_request is not None:
        count -= 1
        if count <= 0:
            return False
        sleep(sleepTime)
    return True

def SendCommand(peripheral, cmdFunc, timeout=0.2, **kwargs):
    """ spin a few cycles wait till the hub is ready to send the command request """
    if okToSendCommand(peripheral, timeout):
        cmdFunc(**kwargs)
    else:
        Log.error('Abort sending command to %s' %(str(cmdFunc)))






