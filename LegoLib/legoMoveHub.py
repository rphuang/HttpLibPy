from pylgbst.hub import MoveHub
from pylgbst.messages import MsgHubProperties
from pylgbst.utilities import usbyte, str2hex

class LegoMoveHub(MoveHub):
    """ extend pylgbst's MoveHub """
    def __init__(self, connection=None):
        """ constructor and get the name and mac address from MoveHub """
        super(LegoMoveHub, self).__init__(connection)
        self.name = self._getName()
        self.mac = self._getMac()

    def getVoltage(self):
        """ get voltage from the hub """
        voltage = self.send(MsgHubProperties(MsgHubProperties.VOLTAGE_PERC, MsgHubProperties.UPD_REQUEST))
        assert isinstance(voltage, MsgHubProperties)
        val = usbyte(voltage.parameters, 0)
        #log.info("Voltage: %s%%", val)
        return val

    def _getName(self):
        """ get name from the hub """
        name = self.send(MsgHubProperties(MsgHubProperties.ADVERTISE_NAME, MsgHubProperties.UPD_REQUEST))
        return name.payload.decode("utf-8")

    def _getMac(self):
        """ get mac address from the hub """
        mac = self.send(MsgHubProperties(MsgHubProperties.PRIMARY_MAC, MsgHubProperties.UPD_REQUEST))
        return str2hex(mac.payload).decode("utf-8")

