import os
import cv2
from .baseCamera import BaseCamera


class Camera(BaseCamera):
    video_source = 0
    width = 1280
    height =720

    def __init__(self, width=1280, height=720, crosshair=False):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        Camera.width = width
        Camera.height = height
        super(Camera, self).__init__(width, height, crosshair=crosshair)

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, Camera.width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Camera.height)
        while True:
            # read current frame
            _, img = camera.read()
            yield img

    @staticmethod
    def createCamera(config):
        """ create a Camera using settings defined in config """
        width = config.getOrAddInt('camera.width', 1280)
        height = config.getOrAddInt('camera.height', 720)
        crosshair = config.getOrAddBool('camera.drawCrosshair', 'true')
        camera = Camera(width=width, height=height, crosshair=crosshair)
        return camera
