#!/usr/bin/python3
# File name   : iotNode.py
# Description : base class for all IOT nodes 

class IotNode(object):
    """ the base class for all IOT nodes """
    def __init__(self, name, parent):
        """ construct an IotNode
        name - the name of the node
        parent - parent IotNode object. None for root node.
        """
        self.name = name
        self.parent = parent

    def fullPathName(self):
        """ get the node's full path name with parent path included """
        if self.parent == None:
            return self.name
        else:
            return self.parent.fullPathName() + '.' + self.name

    def root(self):
        """ get the root IotNode """
        if self.parent == None:
            return self
        else:
            return self.parent.root()

    def startUp(self):
        """ this method should be called once to start up the node before any actions """
        pass

    def shutDown(self):
        """ this method should be called once to shutdown the node """
        pass






