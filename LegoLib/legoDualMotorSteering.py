from IotLib.iotSteering import IotSteering
from .legoNode import SendCommand

class LegoDualMotorSteering(IotSteering):
    """ this class implements steering based on lego's dual motors """
    def __init__(self, name, parent, motor, secondPerDegree=0.003):
        """ construct a steering
        name: the name of the node
        parent: parent IotNode object. None for root node.
        motor: an instance of pylgbst.Motor with dual motors
        secondPerDegree: to control how long it takes to turn one degree (0.003 means 1 seconds to turn 300 degrees)
        """
        self.motor = motor
        self._secondPerDegree = secondPerDegree
        super(LegoDualMotorSteering, self).__init__(name, parent)

    def gotoAngle(self, angle):
        """ move the steering to angle. Return the achieved angle position.
        derived classes must override to move the motor/servo to the angle position. 
        the angle range (in degree): -90 (max left) - 0 (straight) - +90 (max right)
        however, this angle can be clamped to the physical limitation by derived class.
        """
        # calculate time to turn. todo: make constants configurable
        time = 0.18 + (self._secondPerDegree * abs(angle))
        if angle > 0:
            SendCommand(self.motor, self.motor.timed, seconds=time, speed_primary=0.5, speed_secondary=-0.5)
        else:
            SendCommand(self.motor, self.motor.timed, seconds=time, speed_primary=-0.5, speed_secondary=0.5)
        self.angle = angle
        return self.angle

    def gotoCenter(self):
        """ move the steering to center position. Return the achieved angle position.
        derived classes must override to move the motor/servo to the center position. 
        """
        self.angle = 0
        return self.angle

    def move(self, leftSpeed, rightSpeed):
        """ turn/move toward right
        The speed range from -100 to 100.
        """
        SendCommand(self.motor, self.motor.start_power, power_primary=float(leftSpeed) / 100.0, power_secondary=float(rightSpeed) / 100.0)
        #self.motor.start_power(float(leftSpeed) / 100.0, float(rightSpeed) / 100.0)

    def stop(self):
        """ stop the motor """
        SendCommand(self.motor, self.motor.stop, timeout=1.0)
        #self.motor.stop()

    def turn(self, speed, time=0):
        """ use the motor to turn
        the speed range: -100 (left) to 100 (right)
        time: turning time in seconds 
        """
        speed = float(speed) / 100.0
        if time > 0:
            SendCommand(self.motor, self.motor.timed, seconds=time, speed_primary=speed, speed_secondary=-speed)
            #self.motor.timed(time, speed, -speed)
        else:
            SendCommand(self.motor, self.motor.start_power, power_primary=speed, power_secondary=-speed)
            #self.motor.start_power(speed, -speed)

