from .iotNode import IotNode
from .iotRGB import RGB, RGBColors

class IotDrive(IotNode):
    """ the base class for a drive that contains motor, steering, and optional leds"""
    def __init__(self, name, parent, motor, steering, leftLed=None, rightLed=None):
        """ construct a drive 
        name: the name of the node
        parent: parent IotNode object. None for root node.
        motor: an instance of IotMotor
        steering: an instance of IotSteering
        leftLed: the RGB LED on the left
        rightLed: the RGB LED on the right
        """
        super(IotDrive, self).__init__(name, parent)
        self.motor = motor
        self.steering = steering
        self.leftLed = leftLed
        self.rightLed = rightLed
        self.turnSignal = False
        self.extraSpeedOnSteering = 0 # config.getOrAddInt('steering.extraSpeed', 20)

    def stop(self):
        """ stop the motor """
        self.motor.stop()

    def emergencyStop(self):
        """ stop the motor immediately """
        self.motor.emergencyStop()

    def run(self, speed, steeringAngle=0):
        """ move drive with specified speed and steering angle. 
        The speed ranges from -100 (backward) to 0 (stop) to 100 (forward).
        The steering angle ranges from -90 (left) to 0 (straight) to 90 (right) """
        self.steering.gotoAngle(steeringAngle)
        self.motor.run(speed)

    def forward(self, speed):
        """ move drive forward with specified speed. The speed ranges from 0 (stop) to 100 (forward). """
        self.motor.run(speed)

    def backward(self, speed):
        """ move drive backward with specified speed. The speed ranges from 0 (stop) to 100 (backward). """
        self.motor.run(-speed)

    def extraSpeed(self, deltaSpeed):
        """ request extra speed in addition to the run speed """
        self.motor.extraSpeed(deltaSpeed)

    def turnSteering(self, angle, turnSignal=True):
        """ turn the steering to the specified angle
        the angle range (in degree): -90 (max left) - 0 (straight) - +90 (max right)
        however, this angle will be clamped to the physical limitation as defined in constructor.
        the method return the achieved angle position.
        """
        if angle == 0:
            value = self.turnStraight()
        elif angle < 0:
            value = self.turnLeft(-angle, turnSignal)
        else:
            value = self.turnRight(angle, turnSignal)
        return value

    def turnStraight(self):
        """ turn the steering to straight position and turn off led signal
        the method return the achieved angle position.
        """
        value = self.steering.gotoCenter()
        self.motor.extraSteeringSpeed(0)
        if self.turnSignal:
            self.setLedsRGB(RGBColors.RGBOFF, RGBColors.RGBOFF)
            self.turnSignal = False
        return value

    def turnLeft(self, angle):
        """ turn the steering to left and turn on left led signal. angle should be 0 to 90.
        the method return the achieved angle position.
        """
        value = self.steering.gotoAngle(-angle)
        self.motor.extraSteeringSpeed(self.extraSpeedOnSteering)
        if self.turnSignal:
            self.setLedsRGB(RGBColors.YELLOW, RGBColors.RGBOFF)
            self.turnSignal = True
        return value

    def turnRight(self, angle, turnSignal=True):
        """ turn the steering to right and turn on right led signal
        the method return the achieved angle position.
        """
        value = self.steering.gotoAngle(angle)
        self.motor.extraSteeringSpeed(self.extraSpeedOnSteering)
        if self.turnSignal:
            self.setLedsRGB(RGBColors.RGBOFF, RGBColors.YELLOW)
            self.turnSignal = True
        return value

    def setLedsRGB(self, left, right):
        """ method to set left & right LEDs inputs are RGB """
        if not self.leftLed is None:
            self.leftLed.setRGB(left)
        if not self.rightLed is None:
            self.rightLed.setRGB(right)




