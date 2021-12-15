from .iotDualMotor import IotDualMotor

class IotEncodedMotor(IotDualMotor):
    """ the base class for motor with encoder
    The speed range from -100 to 100 with zero (less than minMovingSpeed) to stop the motor.
    """
    def __init__(self, name, parent, minMovingSpeed=5):
        """ construct a PiIotNode
        name: the name of the node
        parent: parent IotNode object. None for root node.
        minMovingSpeed: the minimum valid moving absolute speed
        """
        super(IotEncodedMotor, self).__init__(name, parent, minMovingSpeed)

    def runAngle(self, angle, speed, speed2 = None):
        """ move the motor by specified angle for either single or dual motor
        angle range from 0 to 360 degree
        speed controls the direction ranges from -100 to 100
        """
        pass

    def goToPosition(self, position, position2 = None, speed = 100):
        """ run the motor to specified positions for either single or dual motor
        position range from int.min to int.max
        speed controls the direction ranges from -100 to 100
        """
        pass




