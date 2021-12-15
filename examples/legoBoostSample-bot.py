# simple sample code to run Boost using BoostBot

from time import sleep
from IotLib.config import Config
from LegoLib.boostBot import BoostBot

boostConfig = Config('boostconfig.txt', autoSave=True)
bot = BoostBot('Boost', parent=None, camera=None, config=boostConfig)
bot.connect()
bot.startUp()

# move forward
bot.forward(30)
sleep(3)
bot.stop()
sleep(3)

# turn boost (Vernie) head
bot.turnHead(60, speed=5)
sleep(3)
bot.turnHead(-60, speed=5)
sleep(3)
bot.turnHead(0, speed=5)
sleep(3)

# move backward
bot.backward(30)
sleep(3)
bot.stop()
sleep(3)

# move by position
bot.goToPosition(800, speed=30)
sleep(3)
bot.goToPosition(0, speed=30)
sleep(3)

# moving left
bot.run(30, 40)
sleep(2)
bot.stop()
sleep(3)
# back to original spot
bot.run(-30, -40)
sleep(2)
bot.stop()
sleep(3)

# turn left
bot.run(-30, 30)
sleep(1)
bot.stop()
sleep(3)
# back to original spot
bot.run(30, -30)
sleep(1)
bot.stop()

# turn left
bot.turnLeft(90)
sleep(3)
# back to original spot
bot.turnRight(90)

sleep(5)
bot.shutOff()
