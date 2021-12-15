from time import sleep
import traceback
from pylgbst.hub import MoveHub
from pylgbst import get_connection_gattool, get_connection_auto
from IotLib.pyUtils import startThread
from IotLib.log import Log
from IotLib.iotMobileBot import IotMobileBot
from IotLib.iotDrive import IotDrive
from IotLib.iotBotHead import IotBotHead
try:
    from .legoMoveHub import LegoMoveHub
    from .legoMotor import LegoMotor
    from .legoSteering import LegoSteering
    from .legoDualMotorSteering import LegoDualMotorSteering
    from .legoRGBLed import LegoRGBLed
    from .legoVisionSensor import LegoVisionSensor
except:
    from legoMoveHub import LegoMoveHub
    from legoMotor import LegoMotor
    from legoSteering import LegoSteering
    from legoDualMotorSteering import LegoDualMotorSteering
    from legoRGBLed import LegoRGBLed
    from legoVisionSensor import LegoVisionSensor

class BoostBot(IotMobileBot):
    """ implements a simple robotic controller for lego boost (Vernie) using motors A & B for drive and steering
    additional camera can be mounted on the bot's body to provide video and face tracking functions
    """
    def __init__(self, name, parent, camera, config):
        """ construct a lego boost 
        name: the name of the node
        parent: parent IotNode object. None for root node.
        camera: an instance of PiCamera
        config: config/setting - an instance of Config
        """
        self.hub = None
        self.camera = camera
        super(BoostBot, self).__init__(name, parent, config)

    def connect(self, hub = None):
        """ connect to move hub and initialize the boost 
        """
        moveHub = hub
        if moveHub is None:
            # connect to the move hub
            try:
                conn = get_connection_auto(hub_name='Move Hub')
                moveHub = LegoMoveHub(conn)
            except Exception as e:
                Log.error('Exception connecting to MoveHub: ' + str(e))
                traceback.print_exc()
                conn = get_connection_gattool(hub_name='Move Hub')
                moveHub = LegoMoveHub(conn)
            Log.info('Connected to %s (mac: %s) with battery: %s' %(moveHub.name, moveHub.mac, moveHub.getVoltage()))

        self.hub = moveHub
        self.led = LegoRGBLed('Led', self, self.hub.led)
        minMovingSpeed=self.config.getOrAddInt('motor.minMovingSpeed', 5)
        maxPower=self.config.getOrAddFloat('motor.maxPower', 1.0)
        self.motorAB = LegoMotor('motorAB', self, self.hub.motor_AB,
                              data=LegoMotor.NoData, minMovingSpeed=minMovingSpeed, maxPower=maxPower)
        self.motorA = LegoMotor('motorA', self, self.hub.motor_A, 
                              data=LegoMotor.SpeedData, minMovingSpeed=minMovingSpeed, maxPower=maxPower)
        self.motorB = LegoMotor('motorB', self, self.hub.motor_B,
                              data=LegoMotor.SpeedData, minMovingSpeed=minMovingSpeed, maxPower=maxPower)
        self.motorExt = LegoMotor('motorExt', self, self.hub.motor_external, 
                              data=LegoMotor.AngleData, minMovingSpeed=minMovingSpeed, maxPower=maxPower)
        self.steering = LegoDualMotorSteering('steering', self, self.hub.motor_AB)
        self.drive = IotDrive('drive', self, self.motorAB, self.steering, leftLed=self.led, rightLed=None)
        self.visionSensor = LegoVisionSensor('vision', self, self.hub.vision_sensor)
        self.headSteering = LegoSteering('head steering', self, self.motorExt)
        self.head = IotBotHead('head', self, self.headSteering, None)
        self._initialize(self.drive, self.visionSensor, self.camera, None)

    def startUp(self):
        """ override to start all the components """
        self.motorAB.startUp()
        sleep(0.2)
        self.steering.startUp()
        self.led.startUp()
        self.visionSensor.startUp()
        super(BoostBot, self).startUp()

    def shutDown(self):
        """ override to shut down """
        self.motorAB.shutDown()
        self.steering.shutDown()
        self.led.shutDown()
        self.visionSensor.shutDown()
        super(BoostBot, self).shutDown()

    def shutOff(self):
        """ shutdown and turn off the boost bot """
        self.shutDown()
        if self.hub is not None:
            Log.action('Shutting off %s (battery: %s)' %(self.hub.name, self.hub.getVoltage()))
            self.hub.switch_off()
            self.hub = None

    def run(self, speed, speed2=None):
        """ run the motors with specified speed
        speed: the speed for the motor, speed2: the speed for the secondary motor
        speed > 0 run forward max 100
        speed < 0 run reverse max -100
        speed = 0 stop
        """
        self.motorAB.run(speed, speed2)

    def goToPosition(self, position, speed = 100):
        """ run both motors to specified positions for encoded single or dual motor
        position is in degrees range from int.min to int.max
        speed controls the direction ranges from -100 to 100
        """
        self.motorAB.goToPosition(position, None, speed)

    def goToPositionAsync(self, position, speed = 100):
        """ run both motors to specified positions in separate thread
        position is in degrees range from int.min to int.max
        speed controls the direction ranges from -100 to 100
        """
        self.motorAB.goToPositionAsync(position, None, speed)

    def turnHead(self, angle, speed = 100):
        """ turn head to angle position """
        self.headSteering.gotoAngle(angle, speed)

    def turnHeadAsync(self, angle, speed = 100):
        """ turn head to angle position in separate thread """
        self.headSteering.gotoAngleAsync(angle, speed)

    def _wanderScanAction(self):
        """ scan distance to left and right """
        found = False
        count = 0
        speed = -50
        time = 0.3
        reverse = False
        while True:
            sleep(0.2)
            #Log.debug('WanderScan moving left %f' %time)
            self.steering.turn(speed, time)
            #Log.debug('WanderScan measuring distance')
            sleep(0.2)
            distance = self.visionSensor.distance
            if distance > 0.2:
                found = True
                break
            count += 1
            if count > 6:
                break
            elif count > 3 and not reverse:
                speed = -speed
                reverse = True
        if found:
            self._wanderNextState(IotMobileBot.WanderStateInit)
        else:
            pass

    def _faceTrackingAction(self, xd, yd):
        """ _faceTrackingAction to steering the bot toward the face
        override the parent to use LegoSteering (motorAB) to just move the delta (xd)
        """
        if abs(xd) > 4:
            self.steering.gotoAngle(xd)


