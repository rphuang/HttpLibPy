import cv2
import dlib
import time
from IotLib.log import Log

class FaceTracker():
    """ detect & track faces in sequence of images in bgr format (cv2 format)
    - face detection uses cv2's cascade classifier (cv2.CascadeClassifier) and must be initialized with FaceTracker constructor
    - tracking uses dlib's correlation_tracker

    FaceTracker also defines the base interface for face tracking. The following functions are mandatory:
    - detectOrTrack
    - trackingData
    """
    def __init__(self, faceClassifier, framesForDetection = 10, scaleFactor = 1.1, minNeighbors = 5, trackQualityBar = 8, trackQualityLowBar = 5, trackOffset=10, debug = False):
        """ create an instance of FaceTracker to detect/track faces 
        calling parameters:
        faceClassifier              # classifier for face detection
        framesForDetection = 10     # defines how often the face detection will be run
        scaleFactor = 1.1           # the scale factor for face detection
        minNeighbors = 5            # the MinNeighbors for face detection
        trackQualityBar = 8         # the quality for tracking
        trackQualityLowBar = 5      # the quality to remove for tracking
        trackOffset = 10            # the offset to add to the tracking rectangle
        debug = False               # enable debug information
        """
        self.faceClassifier = faceClassifier
        self.framesForDetection = framesForDetection
        self.scaleFactor = scaleFactor
        self.minNeighbors = minNeighbors
        self.trackQualityBar = trackQualityBar
        self.trackQualityLowBar = trackQualityLowBar
        self.trackOffset = trackOffset
        self.debugMode = debug
        self.boxColor = (0, 255, 0)        # color for the rectangle box around the face
        self.lowBarBoxColor = (0, 0, 255)  # color for the rectangle box around the face
        self.frameCounter = 0              # current frame number
        self.nextFaceID = 0                # sequence ID for face deteced
        self.trackedFaces = {}             # dictionary for the tracked faces' data key=face ID, value=FaceTrackingData 
        self.imageShape = ()               # the image shape for tracked faces

    def detectOrTrack(self, img):
        """ this is the main function for FaceTracker to track the faces inside images
        detectOrTrack returns the image with boxes around all faces tracked
        """

        # 1. update all trackers and remove the ones with lower quality (defined by trackQualityBar)
        # 2. runs face detection for every framesForDetection frames
        #    - for each face try to match an existing tracked faces:
        #      . the face's centerpoint is inside existing tracked box
        #      . the centerpoint of the tracked box is also inside the face's box
        #    - if no match add a new tracker with a new face-id
        fidsToDelete = []
        for fid in self.trackedFaces.keys():
            trackingQuality = self.trackedFaces[fid].update(img)
            if trackingQuality < self.trackQualityLowBar:
                Log.info("Removing face ID " + str(fid) + ' quality: ' + str(trackingQuality))
                fidsToDelete.append(fid)

        for fid in fidsToDelete:
            self.trackedFaces.pop(fid , None)

        # determine whether to run face detection
        if (self.frameCounter % self.framesForDetection) == 0:
            faces = self.detectFaces(img)
            if faces is not None:
                #if self.debugMode and len(faces) != len(self.trackedFaces):
                    #Log.info('Found faces: ' + str(len(faces)) + ' Tracking faces: ' + str(len(self.trackedFaces)))

                for (_x,_y,_w,_h) in faces:
                    # convert to int since dlib requires numpy.int32
                    x = int(_x)
                    y = int(_y)
                    w = int(_w)
                    h = int(_h)
                    #calculate the centerpoint
                    x_center = x + 0.5 * w
                    y_center = y + 0.5 * h

                    matchedFid = None
                    # go thru all the trackers and check if the centerpoint of the face is within the box of a tracker
                    for fid in self.trackedFaces.keys():
                        t_x, t_y, t_w, t_h = self.trackedFaces[fid].getPosition()

                        #calculate the centerpoint
                        t_x_center = t_x + 0.5 * t_w
                        t_y_center = t_y + 0.5 * t_h

                        # check the centerpoint of the face is within the tracker box
                        # plus the centerpoint of the tracker must be within the detected face box 
                        if ((t_x <= x_center <= (t_x + t_w)) and 
                            (t_y <= y_center <= (t_y + t_h)) and 
                            (x <= t_x_center <= (x + w)) and 
                            (y <= t_y_center <= (y + h))):
                            matchedFid = fid

                    if matchedFid is None:
                        Log.info("Creating new face ID " + str(self.nextFaceID))
                        # create and store the tracker 
                        tracker = dlib.correlation_tracker()
                        pad = self.trackOffset
                        tracker.start_track(img, dlib.rectangle(x-pad, y-pad, x+w+pad, y+h+pad))

                        self.trackedFaces[self.nextFaceID] = FaceTrackingData(self.nextFaceID, tracker)

                        # increase nextFaceID counter
                        self.nextFaceID += 1

        # increase the framecounter
        self.frameCounter += 1

        # draw the rectangle around the tracked faces
        for fid in self.trackedFaces.keys():
            t_x, t_y, t_w, t_h = self.trackedFaces[fid].getPosition()
            pad = self.trackOffset
            color = self.boxColor
            if self.trackedFaces[fid].quality < self.trackQualityBar:
                color = self.lowBarBoxColor
            cv2.rectangle(img, (t_x+pad, t_y+pad), (t_x+t_w-pad, t_y+t_h-pad), color, 1)

            if self.debugMode:
                msg = self.trackedFaces[fid].name + '  ' + str(self.trackedFaces[fid].quality)
                cv2.putText(img, msg, (int(t_x), int(t_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        self.imageShape = img.shape
        return img

    def detectFaces(self, img):
        """ detect faces inside the image
        returns list of faces detected
        """
        try:
            grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)   # need a gray image for face detection
            faces = self.faceClassifier.detectMultiScale(grayImg, self.scaleFactor, self.minNeighbors)
            return faces
        except Exception as e:
            #Log.error('Exception detectFaces: ' + str(e))
            return None

    def getTrackedFaces(self):
        """ get the current tracking data - a dictionary of FaceTrackingData with ID as key and FaceTrackingData as value """
        return self.trackedFaces

    def getImageShape(self):
        """ get the image shape for tracked faces """
        return self.imageShape

class FaceTrackingData():
    """ face tracking data that contains:
    tracker: the dlib's correlation_tracker
    id: face id
    name: name for the tracked data
    quality: quality of the tracking
    """
    def __init__(self, id, tracker):
        """ construct a FaceTrackingData with id and correlation_tracker """
        self.name = "ID " + str(id)
        self.id = id
        self.tracker = tracker
        self.quality = 10

    def update(self, image):
        """ correlation_tracker's update() """
        quality = self.tracker.update(image)
        self.quality = quality
        return quality

    def getPosition(self):
        """ get tracked position - returns [x, y, width, height] """
        tracked_position =  self.tracker.get_position()
        x = int(tracked_position.left())
        y = int(tracked_position.top())
        w = int(tracked_position.width())
        h = int(tracked_position.height())
        return [x, y, w, h]

if __name__ == '__main__':
    # initialize face cascade with the frontal face haar cascade
    faceClassifier = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
    camera = cv2.VideoCapture(0)
    tracker = FaceTracker(faceClassifier, trackQualityBar = 8, trackQualityLowBar = 5)
    while camera.isOpened():
        _, frame = camera.read()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        tracker.detectOrTrack(frame)
        cv2.imshow('Face Tracking', frame)

    cv2.destroyAllWindows()

