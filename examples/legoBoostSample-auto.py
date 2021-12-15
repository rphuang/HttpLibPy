# simple sample code to run Boost in auto modes

from time import sleep
from IotLib.config import Config
from LegoLib.boostCommandBot import BoostCommandBot

boostConfig = Config('boostconfig.txt', autoSave=True)
bot = BoostCommandBot('Boost', parent=None, camera=None, config=boostConfig)
bot.connectAndStartUp()

# init to manual mode
bot.doCommand('mode', 'manual')
sleep(3)

# set to follow mode
bot.doCommand('mode', 'follow')
sleep(10)

# set to wander mode
bot.doCommand('mode', 'wander')
sleep(100)
bot.doCommand('mode', 'manual')
sleep(3)

bot.shutOff()
