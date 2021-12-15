from pylgbst import get_connection_gattool, get_connection_auto, get_connection_bluepy
from LegoLib.legoMoveHub import LegoMoveHub
from IotLib.log import Log

hub=LegoMoveHub(get_connection_auto(hub_name='Move Hub'))
#hub=LegoMoveHub(get_connection_gattool(hub_name='Move Hub'))
Log.info('Connected to %s (mac: %s) with battery %s' %(hub.name, hub.mac, hub.getVoltage()))

from time import sleep
from LegoLib.legoMotor import LegoMotor
motor = LegoMotor('MotorExt', None, hub.motor_external, data=LegoMotor.AngleData)
motor.startUp()
motor.runAngleAsync(100, 20)
sleep(3)
motor.runAngle(-100, 30)
motor.runAngle(100, -30)
motor.goToPosition(720, speed=20)
motor.goToPositionAsync(0, speed=20)
sleep(8)

hub.switch_off()

