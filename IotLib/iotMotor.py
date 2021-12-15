#!/usr/bin/python3
# File name   : iotMotor.py
# Description : encapsulates a DC motor connected via Raspberry Pi's GPIO 

from time import sleep
from .log import Log
from .iotNode import IotNode

# motor states:
#  stop - the motor is stop
#  starting - the motor is starting and ramping up to requested speed
#  moving - the motor is moving at the requested speed
#  stopping - the motor is ramping down to stop
MotorStop = 0
MotorStarting = 1
MotorMoving = 2
MotorStopping = 3

class IotMotor(IotNode):
    """ the base class for a motor that defines the interfaces/functions for a basic motor
    The speed range from -100 to 100 with zero (less than minMovingSpeed) to stop the motor.
    """
    def __init__(self, name, parent, minMovingSpeed=5):
        """ construct a PiIotNode
        name: the name of the node
        parent: parent IotNode object. None for root node.
        minMovingSpeed: the minimum valid moving absolute speed
        """
        super(IotMotor, self).__init__(name, parent)
        self._minMovingSpeed = minMovingSpeed
        self.speed = 0
        self._requestedSpeed = 0
        self._extraSpeed = 0
        self._extraSteeringSpeed = 0

    def stop(self):
        """ stop the motor """
        self._requestedSpeed = 0
        return self.speed

    def emergencyStop(self):
        """ stop the motor immediately """
        self._requestedSpeed = 0
        return self.speed

    def run(self, speed):
        """ run the motor with specified speed 
        speed > 0 run forward max 100
        speed < 0 run reverse max -100
        speed = 0 stop
        return the running speed
        """
        self._requestedSpeed = speed
        Log.info('Run motor %s at requested speed %i' %(self.name, speed))
        return self.speed

    def extraSteeringSpeed(self, deltaSpeed):
        """ add extra torque speed for steering in addition to the run speed by run(speed) """
        self._extraSteeringSpeed = deltaSpeed

    def extraSpeed(self, deltaSpeed):
        """ request extra speed in addition to the run speed by run(speed) """
        self._extraSpeed = deltaSpeed

    @staticmethod
    def _clampSpeed(speed):
        if speed > 100:
            return 100
        elif speed < -100:
            return -100
        return speed
