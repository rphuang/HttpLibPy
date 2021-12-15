# simple sample code to run Boost with video streaming on Raspberry Pi

from time import sleep
from IotLib.config import Config
from LegoLib.boostCommandBot import BoostCommandBot
from CameraLib.cameraPi import Camera
from IotLib.pyUtils import startThread
from streamingService import VideoStream

boostConfig = Config('boostconfig.txt', autoSave=True)
bot = BoostCommandBot('Boost', parent=None, camera=None, config=boostConfig)
bot.connectAndStartUp()

# start video streaming in a thread (use browser to view video http://<ipaddress>:8000)
camera = Camera(width=320, height=240, crosshair=True)
port = config.getOrAddInt('video.httpVideoPort', 8000)
streamer = VideoStream('video', parent=None, camera=camera, config=config, debug=True)
streamer.startUp()
videoThread=startThread('VideoStream', target=streamer.httpVideoStreaming, front=True, args=(port,))

# run the bot with wander mode
bot.doCommand('mode', 'wander')
sleep(200)
bot.doCommand('mode', 'manual')
bot.shutOff()

