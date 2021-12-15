from IotLib.log import Log
from IotLib.iotRGBLed import IotRGBLed
from IotLib.iotRGB import RGB, RGBColors
from .legoNode import SendCommand

class LegoRGBLed(IotRGBLed):
    """ concrete class for lego's RGB LED """
    def __init__(self, name, parent, led):
        """ construct a LegoRGBLed
        name: the name of the node
        parent: parent IotNode object. None for root node.
        led: instance of pylgbst.LEDRGB
        """
        self.led = led
        super(LegoRGBLed, self).__init__(name, parent)

    def setRGBStr(self, rgbStr):
        """ set value by a comma separated RGB string. Ex: 0,255,0 """
        red, green, blue = RGB.getRGBListFromRGBStr(rgbStr)
        self.set(red, green, blue)

    def _setRGB(self, rgb):
        """ output to the RGB LED. derived classes must implement to do physical output """
        legoColor = LegoRGBLed._convertToLegoColor(rgb)
        SendCommand(self.led, self.led.set_color, color=legoColor)
        #self.led.set_color(legoColor)

    @staticmethod
    def _convertToLegoColor(rgb):
        """ convert RGB color to lego Color for pylgbst """
        if rgb in LegoRGBLed.LegoColors:
            legocolor = LegoRGBLed.LegoColors.index(rgb)
            if legocolor >= 0:
                return legocolor
        # todo: normalize to standard color
        return 0

    #@staticmethod
    #def _normalizeColorValue(value):

    def _callback(self, named):
        # todo: update self.rgb
        Log.debug("LED Color callback: %s" %named)

    def startUp(self):
        """ override to subscribe the data from lego sensor """
        SendCommand(self.led, self.led.subscribe, callback=self._callback)
        #self.led.subscribe(self._callback)

    def shutDown(self):
        """ override to unsubscribe the data """
        SendCommand(self.led, self.led.unsubscribe, callback=self._callback)
        #self.led.unsubscribe(self._callback)

    # lego colors corresponding the COLOR_* defined in pylgbst 
    LegoColors = [RGBColors.BLACK,
                 RGBColors.PINK,
                 RGBColors.PURPLE,
                 RGBColors.BLUE,
                 RGBColors.LIGHTBLUE,
                 RGBColors.CYAN,
                 RGBColors.GREEN,
                 RGBColors.YELLOW,
                 RGBColors.ORANGE,
                 RGBColors.RED,
                 RGBColors.WHITE ]




