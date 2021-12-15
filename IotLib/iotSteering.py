from .pyUtils import startThread
from .iotNode import IotNode

class IotSteering(IotNode):
    """ the base class for steering a drive to angle position (in degree): -90 (max left) - 0 (straight) - +90 (max right) """
    def __init__(self, name, parent):
        """ construct a steering
        name: the name of the node
        parent: parent IotNode object. None for root node.
        """
        super(IotSteering, self).__init__(name, parent)
        self.angle = 0

    def gotoAngle(self, angle, speed=100):
        """ move the steering to angle.
        derived classes must override to move the motor/servo to the angle position. 
        the angle range (in degree): -90 (max left) - 0 (straight) - +90 (max right)
        however, this angle can be clamped to the physical limitation by derived class.
        optional speed to control the speed for motor based steering
        """
        pass

    def gotoAngleAsync(self, angle, speed=100):
        """ launch a thread to move the steering to angle.
        the angle range (in degree): -90 (max left) - 0 (straight) - +90 (max right)
        however, this angle can be clamped to the physical limitation by derived class.
        optional speed to control the speed for motor based steering
        """
        startThread('%s.gotoAngle' %self.name, target=self.gotoAngle, front=True, args=(angle, speed))

    def gotoCenter(self, speed=100):
        """ move the steering to center position.
        derived classes must override to move the motor/servo to the center position. 
        optional speed to control the speed for motor based steering
        """
        pass

    def gotoCenterAsync(self, speed=100):
        """ launch a thread to move the steering to center position.
        optional speed to control the speed for motor based steering
        """
        startThread('%s.gotoCenter' %self.name, target=self.gotoCenter, front=True, args=(speed, ))




