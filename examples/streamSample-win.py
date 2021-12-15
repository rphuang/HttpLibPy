# simple sample code to streaming video on Windows

from IotLib.log import Log
from IotLib.config import Config
from CameraLib.cameraOpencv import Camera
from streamingService import startVideoStream

configFile = 'videoconfig-win.txt'
Log.action('Loading config file: %s' %configFile)
config = Config(configFile, autoSave=True)

# create camera
Log.action('Creating OpenCV Camera')
camera = Camera.createCamera(config)

Log.action('Launching video streaming')
startVideoStream(camera, config, debug=True)

