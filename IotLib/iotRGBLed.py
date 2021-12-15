from .iotNode import IotNode
from .iotRGB import RGB

class IotRGBLed(IotNode):
    """ the base class for RGB LED
    Note: 0 is off otherwise on
    """
    def __init__(self, name, parent):
        """ construct a IotRGBLed
        name: the name of the node
        parent: parent IotNode object. None for root node.
        """
        super(IotRGBLed, self).__init__(name, parent)
        self.set(RGB.OFF, RGB.OFF, RGB.OFF)

    def get(self):
        """ return list of RGB values"""
        return self.rgb.toRGBList()

    def getRGB(self):
        """ return list of RGB values"""
        return self.rgb

    def getRGBStr(self):
        """ return list of RGB values in string """
        return self.rgb.toRGBStr()

    def on(self):
        """ turn on the RGB Led """
        self.set(RGB.ON, RGB.ON, RGB.ON)

    def off(self):
        """ turn off the RGB Led """
        self.set(RGB.OFF, RGB.OFF, RGB.OFF)

    def set(self, red, green, blue):
        """ set value with RGB on/off values. 0 is off otherwise on. """
        self.rgb = RGB(red, green, blue)
        self._setRGB(self.rgb)

    def setRGB(self, rgb):
        """ set value by RGB object. 0 is off otherwise on. Ex: 0,255,0 """
        red, green, blue = rgb.toRGBList()
        self.set(red, green, blue)

    def setRGBStr(self, rgbStr):
        """ set value by a comma separated RGB string. 0 is off otherwise on. Ex: 0,255,0 """
        red, green, blue = RGB.getOnOffFromRGBStr(rgbStr)
        self.set(red, green, blue)

    def _setRGB(self, rgb):
        """ output to the RGB LED. derived classes must implement to do physical output """
        pass




