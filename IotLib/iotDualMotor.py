from .iotMotor import IotMotor

class IotDualMotor(IotMotor):
    """ the base class for a dual/synchronized motor that defines the interfaces/functions for a basic motor
    The speed range from -100 to 100 with zero (less than minMovingSpeed) to stop the motor.
    """
    def __init__(self, name, parent, minMovingSpeed=5):
        """ construct a PiIotNode
        name: the name of the node
        parent: parent IotNode object. None for root node.
        minMovingSpeed: the minimum valid moving absolute speed
        """
        super(IotDualMotor, self).__init__(name, parent, minMovingSpeed)
        self._requestedSpeed2 = 0
        self.speed2 = 0

    def run(self, speed, speed2=None):
        """ run the motor with specified speeds for two motors if speed2 in None then speed will be used for both motors
        speed: the speed for the motor, speed2: the speed for the secondary motor
        speed > 0 run forward max 100
        speed < 0 run reverse max -100
        speed = 0 stop
        """
        pass




