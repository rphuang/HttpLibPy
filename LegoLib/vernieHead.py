from IotLib.log import Log

forward = FORWARD = right = RIGHT = 1
backward = BACKWARD = left = LEFT = -1
straight = STRAIGHT = 0

class VernieHead():
    def __init__(self, hub):
        self.hub = hub
        self.motor_external = hub.motor_external
        self.motor_AB = hub.motor_AB
        self._head_position = 0
        self.motor_external.subscribe(self._external_motor_data)
        self._reset_head()

    def move(self, direction=RIGHT, angle=25, speed=0.1):
        if direction == STRAIGHT:
            angle = -self._head_position
            direction = 1

        self.motor_external.angled(direction * angle, speed)

    def shot(self):
        self.motor_external.timed(0.5)
        self.move(STRAIGHT)
        self.move(STRAIGHT)

    def _external_motor_data(self, data):
        Log.info("External motor position: %s" %data)
        self._head_position = data

    def _reset_head(self):
        self.motor_external.timed(1, -0.2)
        self.move(RIGHT, angle=45)

