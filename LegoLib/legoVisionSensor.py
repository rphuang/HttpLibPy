from pylgbst.peripherals import COLORS
from IotLib.iotDistanceSensor import IotDistanceSensor
from IotLib.log import Log
from IotLib.iotRGB import RGB
from .legoNode import SendCommand
from .legoRGBLed import LegoRGBLed

class LegoVisionSensor(IotDistanceSensor):
    """ encapsulates a vision sensor for distance and color """
    def __init__(self, name, parent, visionSensor):
        """ construct a LegoVisionSensor
        name: the name of the node
        parent: parent IotNode object. None for root node.
        visionSensor: an instance of pylgbst.VisionSensor
        """
        self.visionSensor = visionSensor
        super(LegoVisionSensor, self).__init__(name, parent)

    def set(self, red, green, blue):
        """ set value with RGB values. """
        self._setRGB(RGB(red, green, blue))

    def setRGB(self, rgb):
        """ set value by RGB object. 0 is off otherwise on. Ex: 0,255,0 """
        self._setRGB(rgb)

    def setRGBStr(self, rgbStr):
        """ set value by a comma separated RGB string. 0 is off otherwise on. Ex: 0,255,0 """
        red, green, blue = RGB.getOnOffFromRGBStr(rgbStr)
        self.set(red, green, blue)

    def _setRGB(self, rgb):
        """ output to the vision sensor's RGB LED. """
        self.rgb = rgb
        legoColor = LegoRGBLed._convertToLegoColor(rgb)
        SendCommand(self.visionSensor, self.visionSensor.set_color, color=legoColor)
        #self.visionSensor.set_color(legoColor)

    def _callback(self, color, distance=None):
        # convert distance in inches to meters
        self.distance = distance * 0.0254
        #Log.debug("%s Color %s, distance %s" %(self.name, str(COLORS[color]), str(self.distance)))
        if self.parent is not None:
            self.parent.checkDistance(self.distance)

    def startUp(self):
        """ override to subscribe the data from lego sensor """
        SendCommand(self.visionSensor, self.visionSensor.subscribe, callback=self._callback)
        #self.visionSensor.subscribe(self._callback)

    def shutDown(self):
        """ override to unsubscribe the data """
        SendCommand(self.visionSensor, self.visionSensor.unsubscribe, callback=self._callback)
        #self.visionSensor.unsubscribe(self._callback)




