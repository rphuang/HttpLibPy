from IotLib.iotSteering import IotSteering

class LegoSteering(IotSteering):
    """ this class implements steering based on lego's encoded motor """
    def __init__(self, name, parent, motor):
        """ construct a steering
        name: the name of the node
        parent: parent IotNode object. None for root node.
        motor: an instance of LegoMotor
        """
        self.motor = motor
        super(LegoSteering, self).__init__(name, parent)

    def gotoAngle(self, angle, speed=100):
        """ move the steering to angle.
        derived classes must override to move the motor/servo to the angle position. 
        the angle range (in degree): -90 (max left) - 0 (straight) - +90 (max right)
        however, this angle can be clamped to the physical limitation by derived class.
        optional speed to control the speed for motor based steering
        """
        self.motor.goToPosition(angle, speed=speed)

    def gotoCenter(self, speed=100):
        """ move the steering to center position.
        derived classes must override to move the motor/servo to the center position. 
        optional speed to control the speed for motor based steering
        """
        self.motor.goToPosition(0, speed=speed)





