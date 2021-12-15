from .iotNode import IotNode

class IotBotHead(IotNode):
    """ the base class for a robotic head with horizontal and/or vertical movements """
    def __init__(self, name, parent, horizontalSteering, verticalSteering):
        """ construct a head 
        name: the name of the node
        parent: parent IotNode object. None for root node.
        horizontalSteering: an instance of IotSteering to move head horizontally
        verticalSteering: an instance of IotSteering to move head vertically
        """
        super(IotBotHead, self).__init__(name, parent)
        self.horizontalSteering = horizontalSteering
        self.verticalSteering = verticalSteering

    def turnStraight(self):
        """ turn both steerings to straight position
        """
        if self.horizontalSteering is not None:
            self.horizontalSteering.gotoCenter()
        if self.verticalSteering is not None:
            self.verticalSteering.gotoCenter()

    def turnHorizontal(self, angle):
        """ turn the horizontal steering to left or right
        """
        if self.horizontalSteering is not None:
            self.horizontalSteering.gotoAngle(angle)

    def turnVertical(self, angle):
        """ turn the vertical steering to up or down
        """
        if self.verticalSteering is not None:
            self.verticalSteering.gotoAngle(angle)



