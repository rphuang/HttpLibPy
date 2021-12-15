#!/usr/bin/python3
# File name   : iotCommon.py
# Description : defines utilities and constants

class RGB():
    """ encapsulates a color """
    # on/off value
    ON  = 1
    OFF = 0

    def __init__(self, red, green, blue):
        """ construct a Color with red, green, blue """
        self.red = red
        self.green = green
        self.blue = blue

    def __eq__(self, other):
        if not isinstance(other, RGB):
            return False
        return self.red == other.red and self.green == other.green and self.blue == other.blue

    def toRGBList(self):
        """ returns list of [red, green, blue] """
        return [self.red, self.green, self.blue]

    def toRGBStr(sef):
        """ return RGB in string format separated by common as 'red, green, blue' """
        return str(self.red) + ', ' + str(self.green) + ', ' + str(self.blue)

    @staticmethod
    def createRGBFromRGBStr(rgbStr):
        """ returns [red, green, blue] that represents whether each led is on or off """
        red, green, blue = rgbStr.split(',')
        return RGB(red, green, blue)

    @staticmethod
    def getRGBListFromRGBStr(rgbStr):
        """ returns [red, green, blue] that represents whether each led is on or off """
        red, green, blue = rgbStr.split(',')
        return [red, green, blue]

    @staticmethod
    def getOnOffFromRGBStr(rgbStr):
        """ returns [red, green, blue] that represents whether each led is on or off """
        red, green, blue = rgbStr.split(',')
        return [RGB.convertToOnOff(red), RGB.convertToOnOff(green), RGB.convertToOnOff(blue)]

    @staticmethod
    def convertToOnOff(strval):
        """ converting none-zero value to ON (1) """
        if int(strval) == 0:
            return RGB.OFF
        else:
            return RGB.ON

class RGBColors():
    # constants for RGB colors
    RGBON = RGB(255, 255, 255)
    RGBOFF = RGB(0, 0, 0)
    RED = RGB(255, 0, 0)
    GREEN = RGB(0, 255, 0)
    BLUE = RGB(0, 0, 255)
    YELLOW = RGB(255, 255, 0)
    PINK = RGB(255, 0, 255)
    CYAN = RGB(0, 255, 255)
    WHITE = RGB(255, 255, 255)
    BLACK = RGB(0, 0, 0)
    PURPLE = RGB(128, 0, 128)
    LIGHTBLUE = RGB(173, 216, 230)
    ORANGE = RGB(255, 165, 0)


