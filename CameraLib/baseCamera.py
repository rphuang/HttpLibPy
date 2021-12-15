import time
import threading
import cv2
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident
from IotLib.log import Log

class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is available."""
    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            Log.info('add camera event with thread id: %s' % ident)
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            Log.info('remove camera event with thread id: %s' % remove)
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        thraedId = get_ident()
        self.events[thraedId][0].clear()


class BaseCamera(object):
    """ base camera class that supports static image frames with muti-threaded clients access
    """
    # todo: break this into two classes - CameraBase and CameraClient to remove the limitation of static image frames
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    trackingFrame = None  # current frame with face tracking is stored here by background thread
    last_access = 0  # time of last client access to the camera
    faceTracker = None  # face tracking object
    event = CameraEvent()

    def __init__(self, width=1280, height=720, crosshair=False):
        """ construct an instance of camera
        crosshair - whether to draw crosshair in the center of each frame
        """
        self.crosshair = crosshair
        self.width = width
        self.height = height
        pass

    def resolution(self):
        """ the resolution of the camera returns (width, height) """
        return (self.width, self.height)

    def start(self, faceTracker=None):
        """Start the background camera thread if it isn't running yet."""
        BaseCamera.faceTracker = faceTracker    # allows enable face tracking after the first non-face tracking instance
        if BaseCamera.thread is None:
            BaseCamera.last_access = time.time()

            # start background frame thread
            BaseCamera.thread = threading.Thread(target=self._thread)
            BaseCamera.thread.start()
            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self, tracking=False):
        """Return the current camera frame, wait till the frame is ready."""
        BaseCamera.last_access = time.time()

        # wait for a signal from the camera thread
        BaseCamera.event.wait()
        BaseCamera.event.clear()

        return self.current_frame(tracking)

    def current_frame(self, tracking=False):
        """Return the current camera frame immediately without wait """
        BaseCamera.last_access = time.time()
        frame = BaseCamera.frame
        if tracking and BaseCamera.faceTracker != None:
            frame = BaseCamera.trackingFrame
        if self.crosshair:
            # draw cross hair in the center
            h, w, c = frame.shape
            xc = (int)(w/2)
            yc = (int)(h/2)
            pix = 16
            cv2.line(frame, (xc - pix, yc), (xc + pix, yc), (0, 255, 0), 1)
            cv2.line(frame, (xc, yc - pix), (xc, yc + pix), (0, 255, 0), 1)
        return frame

    def current_trackingvalues(self):
        """ return the current FaceTrackingData values """
        if BaseCamera.faceTracker != None:
            return BaseCamera.faceTracker.getTrackedFaces().values
        return None

    def current_trackingdata(self):
        """ return the current dictionary of FaceTrackingData (key: id, value: FaceTrackingData) """
        if BaseCamera.faceTracker != None:
            return BaseCamera.faceTracker.getTrackedFaces()
        return None

    @staticmethod
    def frames():
        """"Generator that returns frames from the camera."""
        raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def _thread(cls):
        """Camera background thread."""
        Log.info('Starting camera thread %s' % get_ident())
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            BaseCamera.frame = frame
            if BaseCamera.faceTracker != None:
                BaseCamera.trackingFrame = frame.copy()
                BaseCamera.faceTracker.detectOrTrack(BaseCamera.trackingFrame)

            BaseCamera.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - BaseCamera.last_access > 10:
                frames_iterator.close()
                Log.info('Stopping camera thread due to inactivity %s' % get_ident())
                break
        BaseCamera.thread = None
        BaseCamera.faceTracker = None
