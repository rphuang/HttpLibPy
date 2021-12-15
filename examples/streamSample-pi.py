# simple sample code to streaming video on Raspberry Pi

from IotLib.log import Log
from IotLib.config import Config
from CameraLib.cameraPi import Camera
from streamingService import startVideoStream

configFile = 'videoconfig-pi.txt'
Log.action('Loading config file: %s' %configFile)
config = Config(configFile, autoSave=True)

# create camera
Log.action('Creating Pi Camera')
camera = Camera.createCamera(config)

Log.action('Launching video streaming')
startVideoStream(camera, config, debug=True)

