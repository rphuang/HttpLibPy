from .iotNode import IotNode

class IotDistanceSensor(IotNode):
    """ the base class for a distance sensor """
    def __init__(self, name, parent):
        """ construct a distance sensor
        name: the name of the node
        parent: parent IotNode object. None for root node.
        """
        super(IotDistanceSensor, self).__init__(name, parent)
        self.distance = 0
        pass

    def getDistance(self):
        """ get measured distance from the sensor. derived classes should override to ping the sensor. """
        return self.distance





