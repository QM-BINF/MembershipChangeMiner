
#class that represents a node
class Node:

    #@param resource : Resource object that is represented by the node
    #@param weight : the node's weight
    def __init__(self,resource,weight=1):
        self.resource = resource

        self.weight = weight
        self.ID = resource.getID()


    def getResource(self):
        return self.resource

    def getLabel(self):
        return (self.resource.getLabel())

    def getID(self):
        return self.ID

    def getWeight(self):
        return self.weight

    def setWeight(self,weight):
        self.weight = weight


