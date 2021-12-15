import cv2
from CameraLib import baseCamera, faceTracking
from IotLib.log import Log
from IotLib.iotNode import IotNode
from IotLib.pyUtils import startThread

def startVideoStream(camera, config, debug=False):
    """ start video stream """
    port = config.getOrAddInt('video.httpVideoPort', 8000)
    streamer = VideoStream('video', parent=None, camera=camera, config=config, debug=debug)
    streamer.startUp()
    streamer.runVideoStreaming(port)

def startVideoStreamAsync(camera, config, debug=False):
    """ start video stream in a separate thread """
    port = config.getOrAddInt('video.httpVideoPort', 8000)
    streamer = VideoStream('video', parent=None, camera=camera, config=config, debug=debug)
    streamer.startUp()
    videoThread=startThread('VideoStream', target=streamer.runVideoStreaming, front=True, args=(port,))

class VideoStream(IotNode):
    """ video streaming with optional face tracking """
    def __init__(self, name, parent, camera, config, debug=False):
        """ construct a PiCamera """
        super(VideoStream, self).__init__(name, parent)
        self.camera = camera
        self.config = config
        self.debug = debug

    def startUp(self):
        """ override to start the components """
        width, height = self.camera.resolution()
        # update index.html with proper width and height
        try:
            indexHtmlFile = self.config.getOrAdd('video.indexHtml', '/home/pi/src/VideoLib/templates/index.html')
            with open(indexHtmlFile, "w", encoding="utf-8") as f:
                url = "{{ url_for('video_feed') }}"
                html='<html>  <head> <title>Video Streaming</title> </head> <body> <img src="%s" width="%i" height="%i"> </body></html>' %(url, width, height)
                f.writelines('%s\n' %(html))
        except:
            pass
        self.faceTracker = None
        enableFaceTracking = self.config.getOrAddBool('video.enableFaceTracking', 'true')
        if enableFaceTracking:
            filePath = self.config.getOrAdd('video.classifier', '/home/pi/src/data/haarcascade_frontalface_alt.xml')
            self.classifier = cv2.CascadeClassifier(filePath)
            #self.classifier = cv2.CascadeClassifier('/home/pi/adeept_picar-b/server/data/haarcascade_frontalface_alt.xml')
            self.faceTracker = faceTracking.FaceTracker(self.classifier, debug=self.debug)
            Log.info('Streaming camera (%i x %i) with classifier: %s' %(width, height, filePath))
        else:
            self.faceTracker = None
            Log.info('Streaming camera (%i x %i)' %(width, height))

    def runVideoStreaming(self, port):
        """ run video streaming (flask app) as a web. Should be called from a dedicated thread. """
        Log.info('starting httpVideoStreaming on port %d' %port)
        runVideoStreaming(port, self.camera, tracker=self.faceTracker, debug=self.debug, threaded=True)

from flask import Flask, render_template, Response

_app = Flask(__name__)

# the camera object (derived from BaseCamera) for video capture
_streamingCamera = None
# face tracking object (FaceTracker)
_faceTracker = None

def runVideoStreaming(port, camera, classifier=None, tracker=None, debug=False, threaded=True):
    """ run video streaming (flask app) as a web. calling parameters:
    port: the port number for the http web
    camera: a camera instance that is derived from baseCamera.BaseCamera
    classifier: face tracking with FaceTracker using the specified classifier
    tracker: face tracking object (FaceTracker or instance of derived class)
    debug: whether to run the flask app under debug
    threaded: whether to run flask app threaded
    """
    global _streamingCamera, _faceTracker
    _streamingCamera = camera
    if tracker != None:
        _faceTracker = tracker
    elif classifier != None:
        _faceTracker = FaceTracker(classifier, debug=debug)
    _app.run(host='0.0.0.0', port=port, debug=debug, threaded=threaded, use_reloader=False)

@_app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""
    while True:
        tracking = _faceTracker != None # and opencv_mode != 0
        img = camera.get_frame(tracking)

        # encode as a jpeg image and return it
        frame = cv2.imencode('.jpg', img)[1].tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@_app.route('/video_feed')
def video_feed():
    """ Video streaming route. """
    _streamingCamera.start(_faceTracker)
    return Response(gen(_streamingCamera), mimetype='multipart/x-mixed-replace; boundary=frame')


