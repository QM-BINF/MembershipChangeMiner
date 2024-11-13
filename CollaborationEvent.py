

class CollaborationEvent:

    def __init__(self,resource1, resource2, timestamp, object ):
        self.sourceResource = resource1
        self.targetResource = resource2
        self.eventTimestamp = timestamp
        self.objectList = [object]


    def getEventTimestamp(self):
        return self.eventTimestamp

    """
    Add the object if it isn't already in the object list 
    """
    def addObject(self,object):
        if not object in self.objectList:
            self.objectList.append(object)

    """
    Returns whether this collaboration event concerns both resources 
    """
    def concernsResources(self,resource1,resource2):
        return (((self.sourceResource == resource1)and(self.targetResource == resource2)) or ((self.sourceResource == resource2)and(self.targetResource == resource1)))


    def getTupleFormat(self):
        return (self.sourceResource,self.targetResource)


    """
    Returns whether this collaboration event concerns this resource 
    """
    def concernsResource(self, resource):
        return ((self.sourceResource == resource) or (self.targetResource == resource))