import traceback
from time import sleep
from .pyUtils import startThread
from .log import Log
from .iotNode import IotNode
from .iotRGB import RGB, RGBColors

class IotMobileBot(IotNode):
    """ the base class for a robot with drive (motor and steering), distance sensor, camera, and head (IotBotHead)
    IotMobileBot supports following actions:
        forward - move the bot forward
        backward - move the bot backward
        turnLeft - steer to left
        turnRight - steer to right
        turnStraight - steer to straight
    if head is not None IotMobileBot supports following actions:
        lookUp - turn head up
        lookDown - turn head down
        lookLeft - turn head left
        lookRight - turn head right
        lookStraight - turn head straight
    if distance sensor is not None IotMobileBot supports following auto modes:
        FollowDistanceMode - follow a fix distance to target
        AutoWanderMode - autonomous wander around
    if both camera and distance sensor are not None IotMobileBot supports following auto modes:
        FollowLineMode - follow line on the ground
        FaceTrackingMode - track face and mve head to see the tracked face
    """
    # constants for operation modes
    ManualMode = 0
    FollowDistanceMode = 1      # follow a fix distance to target (using distance sensor)
    FollowLineMode = 2          # follow line on the ground
    AutoWanderMode = 3          # autonomous wander around
    FaceTrackingMode = 4        # track face and mve head to see the tracked face
    # constants for wander states
    WanderStateInit = 0         # this is the initial state to start
    WanderStateMoving = 1       # the robot is moving forward.
    WanderStateStop = 2         # the robot is stopped due to obstacle
    WanderStateScan = 3         # scan distance for surroundings and pick the direction with largest distance
    WanderStateTurn = 4         # start steering to turn to new direction
    WanderStateTurning = 5      # turning to the direction with the best distance. then go to init state.
    WanderStateBack = 6         # move the robot backward if failed to find the best distance from the scan then repeat scan
    WanderStateBacking = 7      # the robot is moving backward

    def __init__(self, name, parent, config):
        """ construct a mobile bot 
        name: the name of the node
        parent: parent IotNode object. None for root node.
        config: config/setting - an instance of Config
        """
        super(IotMobileBot, self).__init__(name, parent)
        self.config = config

    def _initialize(self, drive, distanceSensor, camera, head):
        """ initialize a mobile bot. this should be called by derived class as the 2nd step of constructing a bot.
        drive: an instance of IotDrive
        distanceSensor: an instance of IotDistanceSensor
        head: head of the robot
        """
        self.drive = drive
        self.distanceSensor = distanceSensor
        self.camera = camera
        self.head = head
        self.distanceChecker = True
        self._stopDistance = self.config.getOrAddFloat('distanceChecker.stopDistance', 0.2)       # the distance to stop
        self._slowDistance = self.config.getOrAddFloat('distanceChecker.slowdownDistance', 1.0)       # the distance to stop forward movement

    def startUp(self):
        """ start up functions:
        - stop drive
        - distance scanning thread
        - operation mode managing thread """
        # modes initialization
        self._resetModes()
        # start threads
        if self.config.getOrAddBool('distanceChecker.enableThread', 1):
            self.scanThread=startThread('DistanceChecker', target=self._distanceCheckerWorker)        # thread for distance scan (ultrasonic)
        self.modeThread=startThread('ModeManager', target=self._modeWorker)                 # thread for managing operation modes
        # stop motor, move servos to center, 
        self.stop()
        # turn on green lights
        self.drive.setLedsRGB(RGBColors.GREEN, RGBColors.GREEN)

    def shutDown(self):
        """ stop all components """
        # todo: stop all threads
        self._resetModes()
        self.stop()

    def stop(self):
        """ stop the bot """
        self.drive.stop()

    def forward(self, speed):
        """ move bot forward with specified speed. The speed ranges from 0 (stop) to 100 (forward). """
        self.drive.forward(speed)

    def backward(self, speed):
        """ move drive backward with specified speed. The speed ranges from 0 (stop) to 100 (backward). """
        self.drive.backward(speed)

    def turnLeft(self, angle):
        """ turn the steering to left and turn on left led signal. angle should be 0 to 90.
        the method return the achieved angle position.
        """
        self.drive.turnLeft(angle)

    def turnRight(self, angle):
        """ turn the steering to right and turn on right led signal
        the method return the achieved angle position.
        """
        self.drive.turnRight(angle)

    def turnStraight(self):
        """ turn the steering to straight position and turn off led signal
        the method return the achieved angle position.
        """
        self.drive.turnStraight()

    def lookUp(self, angle):
        """ turn head up """
        if self.head is not None:
            self.head.turnVertical(angle)

    def lookDown(self, angle):
        """ turn head down """
        if self.head is not None:
            self.head.turnVertical(-angle)

    def lookRight(self, angle):
        """ turn head right """
        if self.head is not None:
            self.head.turnHorizontal(angle)

    def lookLeft(self, angle):
        """ turn head left """
        if self.head is not None:
            self.head.turnHorizontal(-angle)

    def lookStraight(self, angle):
        """ turn head straight """
        if self.head is not None:
            self.head.turnStraight(-angle)

    def setOperationMode(self, mode):
        """ set bot's operation mode """
        if mode >= IotMobileBot.ManualMode and mode <= IotMobileBot.FaceTrackingMode:
            Log.action('Set operation mode to %s' %self._intToMode(mode))
            self.mode = mode
            return True
        else:
            Log.error('Invalid operation mode: %i' %mode)
            return False

    def _intToMode(self, mode):
        if mode == IotMobileBot.ManualMode:
            return 'Manual'
        if mode == IotMobileBot.FollowDistanceMode:
            return 'FollowDistance'
        if mode == IotMobileBot.FollowLineMode:
            return 'FollowLine'
        if mode == IotMobileBot.AutoWanderMode:
            return 'AutoWander'
        if mode == IotMobileBot.FaceTrackingMode:
            return 'FaceTracking'

    def _resetModes(self):
        """ initialize bot's modes """
        self.mode = IotMobileBot.ManualMode
        self.distanceChecker = True

    def _stopAuto(self):
        """ internal method to stop auto modes """
        self.mode = IotMobileBot.ManualMode
        self.stop()

    def checkDistance(self, distance):
        stopDistance = self._stopDistance       # the distance to stop
        slowDistance = self._slowDistance       # the distance to stop forward movement
        emergencyStopDistance = self.config.getOrAddFloat('distanceChecker.emergencyStopDistance', 0.1)       # the distance to emergency stop
        headingAngleLimit = self.config.getOrAddInt('distanceChecker.headingAngleLimit', 20)       # the angle limit considered as measuring straight ahead
        minMovingSpeed = self.config.getOrAddInt('motor.minMovingSpeed', 5)
        maxSlowdownSpeed = self.config.getOrAddInt('distanceChecker.maxSlowdownSpeed', 15)
        try:
            if self.distanceChecker: # todo: and not self.head.scanning:
                # check distance to stop drive
                if stopDistance > 0 and distance > 0:
                    # todo: implement heading 
                    #if self.head is not None:
                    #    hAngle, vAngle = self.head.heading
                    #else:
                    #    hAngle, vAngle = (0, 0)
                    hAngle, vAngle = (0, 0)
                    # check forward (speed > 0) and heading before stopping
                    if self.drive.motor.speed > 0 and abs(hAngle) < headingAngleLimit and abs(vAngle) < headingAngleLimit:
                        if distance < emergencyStopDistance:
                            Log.info('checkDistance - Emergency Stop drive at distance: %f' %distance)
                            self.drive.emergencyStop()
                            self.drive.extraSpeed(0)
                        elif distance < stopDistance:
                            Log.info('checkDistance - Stopping drive at distance: %f' %distance)
                            self.drive.stop()
                            self.drive.extraSpeed(0)
                        elif distance < slowDistance:
                            slowdown = int((abs(self.drive.motor._requestedSpeed) - minMovingSpeed) * (slowDistance - distance) / (slowDistance - stopDistance))
                            slowdown = -min(slowdown, maxSlowdownSpeed)
                            Log.info('checkDistance - Slowing down %i at distance: %f' %(slowdown, distance))
                            self.drive.extraSpeed(slowdown)

        except Exception as e:
            Log.error('Exception in DistanceChecker: ' + str(e))

    def _distanceCheckerWorker(self):
        """ internal thread for measuring/checking distance at specified interval """
        interval = self.config.getOrAddFloat('distanceChecker.scanCycleInSecond', 0.2)             # delay interval for the worker
        while True:
            distance = self.distanceSensor.getDistance()
            if distance < 0:
                # give it one more try
                distance = self.distanceSensor.getDistance()
            if distance >= 0:
                self.checkDistance(distance)

            sleep(interval)

    def _initMode(self, mode):
        """ initialization of the mode - will be called only when first time switch to the mode """
        if mode == IotMobileBot.ManualMode:
            # stop auto mode when switching from auto to manual mode
            self._stopAuto()
        elif mode == IotMobileBot.FollowDistanceMode:
            if self.head is not None:
                self.head.lookStraight()
            self.drive.turnStraight()
            self._stopDistance = self.config.getOrAddFloat('follow.followDistance', 0.2)       # use the follow distance to stop
            self._slowDistance = self.config.getOrAddFloat('follow.slowdownDistance', 1.0)     # the distance to stop forward movement
            self.distanceChecker = True    # make sure distance scan worker thread to stop before hitting obstacle
        elif mode == IotMobileBot.FollowLineMode:
            pass
        elif mode == IotMobileBot.AutoWanderMode:
            self._wanderState = IotMobileBot.WanderStateInit   # wander states: 0-init, 1-move, 2-stop, 3-scan, 4-turn, 5-back
            self._wanderOldState = IotMobileBot.WanderStateInit
            self._wanderTimeoutCounter = 0
            self._wanderDelay = int(self.config.getOrAddFloat('wander.stateDelayInSecond', 2.0) / 0.2)
            self._wanderDelayCounter = self._wanderDelay
            self.distanceChecker = True    # make sure distance scan worker thread to stop before hitting obstacle
        elif mode == IotMobileBot.FaceTrackingMode:
            self._faceId = -1       # valid face ID should be >= 0

    def _stopMode(self, mode):
        """ initialization of the mode - will be called only when switching off the mode """
        if mode == IotMobileBot.ManualMode:
            pass
        elif mode == IotMobileBot.FollowDistanceMode:
            self.stop()
            self._stopDistance = self.config.getOrAddFloat('distanceChecker.stopDistance', 0.2)       # the distance to stop
            self._slowDistance = self.config.getOrAddFloat('distanceChecker.slowdownDistance', 1.0)       # the distance to stop forward movement
        elif mode == IotMobileBot.FollowLineMode:
            self.stop()
        elif mode == IotMobileBot.AutoWanderMode:
            self.stop()
        elif mode == IotMobileBot.FaceTrackingMode:
            pass

    def _modeWorker(self, interval=0.2):
        """ internal thread for handling bot's operation modes """
        oldMode = self.mode
        while True:
            try:
                if oldMode != self.mode:
                    # mode change - stop old mode and init new mode
                    self._stopMode(oldMode)
                    self._initMode(self.mode)
                if self.mode == IotMobileBot.ManualMode:
                    pass
                elif self.mode == IotMobileBot.FollowDistanceMode:
                    self._followByDistance()
                elif self.mode == IotMobileBot.FollowLineMode:
                    self._followLine()
                elif self.mode == IotMobileBot.AutoWanderMode:
                    self._wander(interval)
                elif self.mode == IotMobileBot.FaceTrackingMode:
                    self._faceTracking()
                else:
                    self._stopAuto()
                oldMode = self.mode
            except Exception as e:
                Log.error('Exception in %s Mode Control: %s' %(self._intToMode(self.mode), str(e)))
                traceback.print_exc()
            sleep(interval)

    def _followByDistance(self):
        """ internal function for followDistance mode
        follow with Ultrasonic by keeping the same distance to target
        this function leverage _distanceCheckerWorker to stop 
        """
        maxDistance = self.config.getOrAddFloat('follow.maxFollowDistance', 2.0)
        dis = self.distanceSensor.getDistance()
        if dis < maxDistance:             #Check if the target is in diatance range
            distanceToFollow = self._stopDistance        # keep the distance to the target set during _initMode
            distanceOffset = self.config.getOrAddFloat('follow.distanceOffset', 0.1)    # controls the sensitivity
            if dis > (distanceToFollow + distanceOffset) :   #If the target is in distance range and out of distanceToFollow, then move forward
                if self.drive.motor.speed > 0:
                    pass
                else:
                    Log.info('followByDistance - move forward. distance: %s' %dis)
                    self.drive.forward(self.config.getOrAddInt('auto.forwardSpeed', 60))
                    self.drive.setLedsRGB(RGBColors.CYAN, RGBColors.CYAN)
            elif dis < (distanceToFollow - distanceOffset) : #Check if the target is too close, if so, the car move back to keep distance at distance
                if self.drive.motor.speed < 0:
                    pass
                else:
                    Log.info('followByDistance - move backward. distance: %s' %dis)
                    self.drive.backward(self.config.getOrAddInt('auto.backwardSpeed', 60))
                    self.drive.setLedsRGB(RGBColors.PINK, RGBColors.PINK)
            else:                            #If the target is at distance, then the car stay still
                if self.drive.motor.speed < 0:
                    # only stop the drive if was backing away
                    Log.info('followByDistance - stop backward. distance: %s' %dis)
                    self.drive.stop()
                    self.drive.setLedsRGB(RGBColors.GREEN, RGBColors.GREEN)
        else:
            if abs(self.drive.motor.speed) > 5:
                Log.info('followByDistance - stop. distance: %s' %dis)
                self.drive.stop()

    def _followLine(self):
        left, middle, right = self.lineTracking.status()
        if middle:
            self.drive.run(speed=self.config.getOrAddInt('auto.forwardSpeed', 60), steeringAngle=0)
            self.drive.setLedsRGB(RGBColors.YELLOW, RGBColors.YELLOW)
        elif left:
            self.drive.forward(speed=self.config.getOrAddInt('auto.forwardSpeed', 60))
            self.drive.turnLeft(angle=45, turnSignal=True)
        elif right:
            self.drive.forward(speed=self.config.getOrAddInt('auto.forwardSpeed', 60))
            self.drive.turnRight(angle=45, turnSignal=True)
        else:
            self.drive.backward(speed=self.config.getOrAddInt('auto.backwardSpeed', 60))
            self.drive.setLedsRGB(RGBColors.CYAN, RGBColors.CYAN)

    def _wander(self, interval):
        """ autonomous wander around mindlessly
        """
        if self._wanderDelayCounter > 1:
            self._wanderDelayCounter -= 1
            return
        self._wanderDelayCounter = 0
        if self._wanderState == IotMobileBot.WanderStateInit:
            # start move forward
            if self.head is not None:
                self.head.lookStraight()
            self.drive.forward(speed=self.config.getOrAddInt('auto.forwardSpeed', 60))
            self._wanderNextState(IotMobileBot.WanderStateMoving)
        elif self._wanderState == IotMobileBot.WanderStateMoving:
            # check whether the drive stopped
            if abs(self.drive.motor.speed) == 0:
                self._wanderNextState(IotMobileBot.WanderStateStop)
        elif self._wanderState == IotMobileBot.WanderStateStop:
            # for now, just move backward
            self._wanderNextState(IotMobileBot.WanderStateBack)
        elif self._wanderState == IotMobileBot.WanderStateScan:
            # scan distance
            self._wanderScanAction()
        elif self._wanderState == IotMobileBot.WanderStateTurn:
            # turn to new direction
            self.drive.turnSteering(self._wanderTurnAngle)
            self.drive.backward(self.config.getOrAddInt('wander.turnSpeed', 60))
            self._wanderTimer = int(self.config.getOrAddFloat('wander.turningTime', 2) / interval)
            self._wanderNextState(IotMobileBot.WanderStateTurning)
        elif self._wanderState == IotMobileBot.WanderStateTurning:
            # count down the timer then stop and go to init state
            self._wanderTimer -= 1
            if self._wanderTimer == 0:
                self.drive.stop()
                self._wanderNextState(IotMobileBot.WanderStateInit)
        elif self._wanderState == IotMobileBot.WanderStateBack:
            # move backward
            self.drive.backward(self.config.getOrAddInt('auto.backwardSpeed', 60))
            self._wanderTimer = int(self.config.getOrAddFloat('wander.backwardTime', 1) / interval)
            self._wanderNextState(IotMobileBot.WanderStateBacking)
        elif self._wanderState == IotMobileBot.WanderStateBacking:
            # count down the timer then stop
            self._wanderTimer -= 1
            if self._wanderTimer == 0:
                self.drive.stop()
                self._wanderNextState(IotMobileBot.WanderStateScan)
        self._wanderTimeoutCounter += 1
        if self._wanderOldState != self._wanderState:
            self._wanderTimeoutCounter = 0
        self._wanderOldState = self._wanderState
        if self._wanderTimeoutCounter > int(self.config.getOrAddFloat('wander.stateTimeout', 10) / interval):
            self.drive.stop()
            Log.warning('Wander timeout go to scan state')
            self._wanderState = IotMobileBot.WanderStateScan
        pass

    def _wanderNextState(self, newState):
        """ switch to new state by adding delay for non-moving states """
        if newState in (IotMobileBot.WanderStateMoving, IotMobileBot.WanderStateTurning, IotMobileBot.WanderStateBacking):
            self._wanderDelayCounter = 0
        else:
            self._wanderDelayCounter = self._wanderDelay
        self._wanderState = newState
        Log.info('Wander state %i' %self._wanderState)
    
    def _wanderScanAction(self):
        """ scan distance to left and right """
        starth = self.config.getOrAddInt('wander.scan.starth', -90)
        startv = self.head.servoV.angle     # use currently vertical angle
        endh = self.config.getOrAddInt('wander.scan.endh', 90)
        endv = startv
        inch = self.config.getOrAddInt('wander.scan.inc', 10)
        incv = inch
        value, posh, posv = self.head.scan(starth, startv, endh, endv, inch, incv)
        Log.info('Scan: %s' %(str(value)))
        # find max
        max = 0
        maxindex = -1
        index = 0
        stopDistance = self._stopDistance
        for val in value:
            if val > max and val > stopDistance:
                max = val
                maxindex = index
            index += 1
        if maxindex > -1:
            # found good one and turning to that direction
            angle = posh[maxindex]
            Log.info('maxindex %i value %f posh %i' %(maxindex, max, angle))
            if angle > 0:
                angle = -self.config.getOrAddInt('wander.turnAngle', 30)
            else:
                angle = self.config.getOrAddInt('wander.turnAngle', 30)
            self._wanderTurnAngle = angle
            self._wanderNextState(IotMobileBot.WanderStateTurn)
        else:
            # cannot find good one so move back
            self._wanderNextState(IotMobileBot.WanderStateBack)

    def _faceTracking(self):
        """ tracking a face by moving head to follow the face """
        if self.camera is None:
            return
        faceTracker = self.camera.faceTracker
        trackedFaces = faceTracker.getTrackedFaces()
        if len(trackedFaces) == 0:
            if self._faceId < 0:
                # todo: searching faces by looking left/right
                pass
            return
        if self._faceId in trackedFaces:
            faceTrackingData = trackedFaces[self._faceId]
        #elif self._faceId < 0:
        else:
            # get the first face tracked
            self._faceId = next(iter(trackedFaces))
            faceTrackingData = trackedFaces[self._faceId]
            Log.info('Start tracking face ID %i' %self._faceId)
            # lost the tracked face
            #Log.debug('Lost tracked face ID %i' %self._faceId)
            #return
        # find the center of the tracked face
        x, y, w, h = faceTrackingData.getPosition()
        x = int(x + w / 2)
        y = int(y + h / 2)
        # center of the image
        imageHeight, imageWidth, c = faceTracker.getImageShape()
        xc = int(imageWidth / 2)
        yc = int(imageHeight / 2)
        # calculate angles to move
        xd = int(((x - xc) / imageWidth) * self.config.getOrAddInt('faceTracking.horizontalViewAngle', 54))
        yd = int(((yc - y) / imageHeight) * self.config.getOrAddInt('faceTracking.verticalViewAngle', 42))
        #Log.debug('x: %i y: %i xc: %i yc: %i xd: %i yd: %i' %(x, y, xc, yc, xd, yd))
        self._faceTrackingAction(xd, yd)

    def _faceTrackingAction(self, xd, yd):
        """ _faceTrackingAction to move the bot toward the face """
        xAngle, yAngle = self.head.heading
        if abs(xd) > 5:
            angle = xAngle + xd
            #Log.debug('Move head horizontal by %i degree to %i degree' %(xd, angle))
            self.head.moveHorizontal(angle)
        if abs(yd) > 5:
            angle = yAngle + yd
            #Log.debug('Move head vertical by %i degree to %i degree' %(yd, angle))
            self.head.moveVertical(angle)
