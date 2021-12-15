#!/usr/bin/python3
# File name   : boostCommandBot.py
# Description : handles commands for boost robots

import traceback

from IotLib.log import Log
from IotLib.iotMobileBot import IotMobileBot
from .boostBot import BoostBot

class BoostCommandBot(BoostBot):
    """ BoostCommandBot extends BoostBot to handle commands for Boost Bots """
    def __init__(self, name, parent, camera, config):
        """ constructor with a Boost Bots object as command target """
        super(BoostCommandBot, self).__init__(name, parent, camera, config)

    def connectAndStartUp(self, hub = None):
        """ connect and start up the boost bot
        returns (statusCode, statusMessage)
        """
        try:
            Log.action('Connect and starting Boost MoveHub')
            self.config.autoSave = False    # disable autoSave (to avoid save multiple times)
            # connect and start up the boost bot
            self.connect(hub)
            self.startUp()
            # initialize members
            self.led = self.drive.leftLed
            self.extMotor = None # self.extMotor
            self.tilt = None # self.tilt
            # enable config auto save and save changes
            self.config.autoSave = True
            self.config.save()
            statusCode = 200
            response = 'Boost MoveHub Connected '
        except Exception as e:
            Log.error('Exception starting Boost: ' + str(e))
            traceback.print_exc()
            statusCode = 500
            response = 'Exception: ' + str(e)
        return (statusCode, response)

    def doCommand(self, cmdPath, valueStr):
        """ execute the command specified by the cmdPath and value
        returns (statusCode, statusMessage)

        valid cmdPath:
        - motorAB: set both A B motor speed or position
        - motorA: set motor A speed or position
        - motorB: set motor B speed or position
        - motorExt: set external motor speed or position
        - steering: set steering position
        - led: boost move hub LED with red, green, blue colors
        - vision: vision sensor LED with red, green, blue colors
        use .pos in the cmdPath to specify the position of the motor example: motorA.pos
        """
        pathLowerCase = cmdPath.lower()
        commandStatus = cmdPath
        httpStatusCode = 400
        response = None
        #Log.debug(' value: ' + valueStr)
        if valueStr != None:
            try:
                # process based on path
                httpStatusCode = 200
                if 'stop' in pathLowerCase:
                    self.stop()
                elif 'forward' in pathLowerCase:
                    self.forward(int(valueStr))
                elif 'backward' in pathLowerCase:
                    self.backward(int(valueStr))
                elif 'right' in pathLowerCase:
                    self.turnRight(int(valueStr))
                elif 'left' in pathLowerCase:
                    self.turnLeft(int(valueStr))
                elif 'motorab' in pathLowerCase:
                    self._doMotorCommand(self.motorAB, pathLowerCase, valueStr)
                elif 'motora' in pathLowerCase:
                    self._doMotorCommand(self.motorA, pathLowerCase, valueStr)
                elif 'motorb' in pathLowerCase:
                    self._doMotorCommand(self.motorB, pathLowerCase, valueStr)
                elif 'motorext' in pathLowerCase:
                    self._doMotorCommand(self.motorExt, pathLowerCase, valueStr)
                elif 'steering' in pathLowerCase:
                    # turn steering with speed, from -100 (left) to 100 (right)
                    speed = int(valueStr)
                    self.steering.turn(speed)
                    if speed > 0:
                        commandStatus = 'Turn Right'
                    elif speed < 0:
                        commandStatus = 'Turn Left'
                    else:
                        commandStatus = 'Turn Straight'
                elif 'led' in pathLowerCase:
                    # for each color: 0 is off non-0 is on
                    self.led.setRGBStr(valueStr)
                    commandStatus = 'Set Led Color'
                elif 'vision' in pathLowerCase:
                    # for each color: 0 is off non-0 is on
                    self.visionSensor.setRGBStr(valueStr)
                    commandStatus = 'Set Vision Sensor Color'
                elif 'mode' in pathLowerCase:
                    # setting mode
                    response = self._doSetModeCommand(valueStr)
                    commandStatus = 'Set Mode to %s' %valueStr
                else:
                    commandStatus = 'Unknown Device Component'
                    httpStatusCode = 400
            except Exception as e:
                # todo: classify different exceptions and http status codes
                Log.error('Exception handling request: ' + str(e))
                traceback.print_exc()
                commandStatus = 'Exception'
                httpStatusCode = 400

        if response == None:
            response = (httpStatusCode, commandStatus)
            
        return response

    def _doMotorCommand(self, motor, pathLowerCase, valueStr):
        """ command posted to a motor """
        if '.pos' in pathLowerCase:
            self._doMotorPositionCommand(motor, valueStr)
        else:
            self._doMotorSpeedCommand(motor, valueStr)

    def _doMotorPositionCommand(self, motor, valueStr):
        """ command posted to a motor position in format: position, speed """
        position, speed = self._getDualValues(valueStr)
        if speed is None:
            speed = self.config.getOrAddInt('auto.defaultSpeed', 90)
        motor.goToPositionAsync(position, position2 = None, speed = speed)

    def _doMotorSpeedCommand(self, motor, valueStr):
        """ command posted to a motor speed in format: speed, speed2
        motor speed range: -100 - 0 - +100 (in %)
        """
        speed, speed2 = self._getDualValues(valueStr)
        if speed == 0:
            motor.stop()
            commandStatus = 'Stop'
        elif speed < 0:
            motor.run(speed, speed2)
            commandStatus = 'Backward'
        else:
            motor.run(speed, speed2)
            commandStatus = 'Forward'
        return commandStatus

    def _getDualValues(self, valueStr):
        """ get single or dual values """
        if isinstance(valueStr, str) and ',' in valueStr:
            # valueStr contains two values for dual motor
            items = valueStr.split(',')
            value = int(items[0])
            value2 = None
            if len(items) > 1:
                value2 = int(items[1])
        else:
            value = int(valueStr)
            value2 = None
        return value, value2

    def _doSetModeCommand(self, valueStr):
        """ command to set mode specified in valueStr
        available modes are: manual, follow, findline, speech, opencv
        returns a dictionary of scan result
        - statusCode
        - response
        """
        valueStrLower = valueStr.lower()
        if 'manual' in valueStrLower:
            self.setOperationMode(IotMobileBot.ManualMode)
        elif 'followline' in valueStrLower:
            self.setOperationMode(IotMobileBot.FollowLineMode)
        elif 'follow' in valueStrLower:
            self.setOperationMode(IotMobileBot.FollowDistanceMode)
        elif 'wander' in valueStrLower:
            self.setOperationMode(IotMobileBot.AutoWanderMode)
        elif 'face' in valueStrLower:
            self.setOperationMode(IotMobileBot.FaceTrackingMode)
        elif 'speech' in valueStrLower:
            self.setOperationMode(IotMobileBot.ManualMode)
        else:
            return (400, 'InvalidMode')
        return (200, 'SetMode %s' %valueStr)



