from threading import RLock
from pylgbst.peripherals import EncodedMotor
from IotLib.pyUtils import startThread
from IotLib.log import Log
from IotLib.iotMotor import IotMotor
from IotLib.iotEncodedMotor import IotEncodedMotor
from .legoNode import SendCommand

# todo: LegoMotor inherits both IotMotor and IotSteering.

class LegoMotor(IotEncodedMotor):
    """ the class encapsulates a lego encoded motor based on pylgbst.Motor
    """
    # subscribe data
    NoData = 0          # do not subscribe data
    SpeedData = 1       # subscribe speed data
    AngleData = 2       # subscribe angle data

    def __init__(self, name, parent, motor, data=0, minMovingSpeed=5, maxPower=1.0):
        """ construct a LegoMotor
        name: the name of the node
        parent: parent IotNode object. None for root node.
        motor: an instance of pylgbst.Motor
        data: which data to subscribe (NoData, SpeedData, or AngleData)
        minMovingSpeed: the minimum valid moving absolute speed
        maxPower: max power allowed for the motor
        """
        super(LegoMotor, self).__init__(name, parent, minMovingSpeed=minMovingSpeed)
        self.motor = motor
        self.data = data
        self.maxPower = maxPower
        self._motorControlLock = RLock()    # lock is required in case of emergencyStop() been called in separate thread

    def stop(self):
        """ stop the motor """
        self._stop()
        return self.speed

    def run(self, speed, speed2=None):
        """ run the motor with specified speed
        speed: the speed for the motor, speed2: the speed for the secondary motor
        speed > 0 run forward max 100
        speed < 0 run reverse max -100
        speed = 0 stop
        return the running speed
        """
        self._requestedSpeed = speed
        self._requestedSpeed2 = speed2
        Log.info('Request %s to run at speed %i, %s' %(self.name, speed, str(speed2)))
        self._run(speed, speed2)
        return self.speed

    def runAngle(self, angle, speed, speed2 = None):
        """ move the motor by specified angle for encoded single or dual encoded motor
        angle is in degree (360 is one rotation)
        speed controls the direction ranges from -100 to 100
        """
        outspd = float(IotMotor._clampSpeed(speed)) / 100.0
        outspd2 = speed2
        if speed2 is not None:
            outspd2 = float(IotMotor._clampSpeed(speed2)) / 100.0
        Log.info('MoveAngle %s by %i degrees at speed %f, %s' %(self.name, angle, outspd, str(outspd2)))
        self._motorControlLock.acquire
        SendCommand(self.motor, self.motor.angled, degrees=angle, speed_primary=outspd, speed_secondary=outspd2, max_power=self.maxPower)
        #self.motor.angled(angle, outspd, outspd2, max_power=self.maxPower)
        self._motorControlLock.release

    def runAngleAsync(self, angle, speed, speed2 = None):
        """ launch a thread to move the motor by specified angle for encoded single or dual motor
        angle is in degree (360 is one rotation)
        speed controls the direction ranges from -100 to 100
        """
        startThread('%s.moveAngle' %self.name, target=self.runAngle, front=True, args=(angle, speed, speed2))

    def goToPosition(self, position, position2 = None, speed = 100):
        """ run the motor to specified positions for encoded single or dual motor
        positions are in degrees range from int.min to int.max
        speed controls the direction ranges from -100 to 100
        """
        outspd = float(IotMotor._clampSpeed(speed)) / 100.0
        Log.info('GoToPosition %s to (%i, %s) at speed %f' %(self.name, position, str(position2), outspd))
        self._motorControlLock.acquire
        SendCommand(self.motor, self.motor.goto_position, degrees_primary=position, degrees_secondary=position2, speed=outspd, max_power=self.maxPower)
        #self.motor.goto_position(position, position2, outspd, max_power=self.maxPower)
        self._motorControlLock.release

    def goToPositionAsync(self, position, position2 = None, speed = 100):
        """ launch a thread to run the motor to specified positions for encoded single or dual motor
        positions are in degrees range from int.min to int.max
        speed controls the direction ranges from -100 to 100
        """
        startThread('%s.goToPosition' %self.name, target=self.goToPosition, front=True, args=(position, position2, speed))

    def extraSpeed(self, deltaSpeed):
        """ request extra speed in addition to the run speed by run(speed) """
        self._extraSpeed = deltaSpeed
        if self.speed2 is not None and self.speed2 != self.speed:
            return
        if self._requestedSpeed == 0 or self.speed == 0:
            return
        absRequestedSpeed = abs(self._requestedSpeed)
        extraSpeed = self._extraSpeed + self._extraSteeringSpeed
        absRunSpeed = abs(self._requestedSpeed) + extraSpeed
        if absRunSpeed != abs(self.speed):
            if self._requestedSpeed > 0:
                self._run(absRunSpeed)
            else:
                self._run(-absRunSpeed)

    def _stop(self):
        """ internal method to stop the motor """
        self._requestedSpeed = 0
        self._requestedSpeed2 = 0
        Log.info('Stop %s' %self.name)
        self._motorControlLock.acquire
        SendCommand(self.motor, self.motor.start_power, power_primary=0, power_secondary=0)
        #self.motor.start_power(0)
        self._motorControlLock.release
        self.speed = 0
        self.speed2 = 0
        return self.speed

    def _run(self, speed, speed2=None):
        """ internal method to run the motor with specified speed 
        speed > 0 run forward max 100
        speed < 0 run reverse max -100
        speed = 0 stop
        return the running speed
        """
        if abs(speed) < self._minMovingSpeed: # stop
            self._stop()
            outspd = 0
            outspd = 0
        else:
            outspd = float(IotMotor._clampSpeed(speed)) / 100.0
            outspd2 = speed2
            if speed2 is not None:
                outspd2 = float(IotMotor._clampSpeed(speed2)) / 100.0
            Log.info('Run %s at speed %f, %s' %(self.name, outspd, str(outspd2)))
            self._motorControlLock.acquire
            SendCommand(self.motor, self.motor.start_speed, speed_primary=outspd, speed_secondary=outspd2, max_power=self.maxPower)
            #self.motor.start_speed(outspd, outspd2, max_power=self.maxPower)
            self._motorControlLock.release
        if self.data == LegoMotor.NoData:
            self.speed = outspd
            self.speed2 = outspd2

    def _callbackSpeed(self, param1):
        Log.debug("Motor %s speed %s" %(self.name, str(param1)))
        self.speed = param1

    def _callbackAngle(self, param1):
        Log.debug("Motor %s angle %s" %(self.name, str(param1)))
        self.angle = param1

    def startUp(self):
        """ override to subscribe the data from lego sensor """
        if self.data == LegoMotor.SpeedData:
            self.motor.subscribe(self._callbackSpeed, mode=EncodedMotor.SENSOR_SPEED, granularity=1)
        elif self.data == LegoMotor.AngleData:
            self.motor.subscribe(self._callbackAngle, mode=EncodedMotor.SENSOR_ANGLE, granularity=1)

    def shutDown(self):
        """ override to unsubscribe the data """
        if self.data == LegoMotor.SpeedData:
            self.motor.unsubscribe(self._callbackSpeed)
        elif self.data == LegoMotor.AngleData:
            self.motor.unsubscribe(self._callbackAngle)



