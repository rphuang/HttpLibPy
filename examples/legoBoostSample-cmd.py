# simple sample code to run Boost using BoostCommandBot

from time import sleep
from IotLib.config import Config
from LegoLib.boostCommandBot import BoostCommandBot

boostConfig = Config('boostconfig.txt', autoSave=True)
bot = BoostCommandBot('Boost', parent=None, camera=None, config=boostConfig)
bot.connectAndStartUp()

# move forward
bot.doCommand('forward', '30')
sleep(3)
bot.stop()
sleep(3)

# turn boost (Vernie) head
bot.doCommand('motorext.pos', '60, 5')
sleep(3)
bot.doCommand('motorext.pos', '-60, 5')
sleep(3)
bot.doCommand('motorext.pos', '0, 5')
sleep(3)

# move backward
bot.doCommand('backward', '30')
sleep(3)
bot.stop()
sleep(3)
# move by position
bot.doCommand('motorab.pos', '800, 30')
sleep(8)
bot.doCommand('motorab.pos', '0, 30')
sleep(3)

# turning left
bot.doCommand('motorab', '-30, 30')
sleep(1)
bot.stop()
sleep(3)
# turning right
bot.doCommand('motorab', '30, -30')
sleep(1)
bot.stop()
sleep(3)

# moving left
bot.doCommand('motorab', '30, 40')
sleep(2)
bot.stop()
sleep(3)
# back to original spot
bot.doCommand('motorab', '-30, -40')
sleep(2)
bot.stop()

sleep(5)
bot.shutOff()


