#class that represents a collaboration session object




class CollaborationSession:

    """
    @param resource1: Resource object representing the first resource
    @param resource2: Resource object representing the second resource
    @param object: Object object representing the object of collaboration
    @param firstTimestamp: date time object indicating the beginning of the window
    @param lastTimestamp: date time object indicating the end of the window
    @param medianTimestamp: date time object indicating the median timestamp in the window
    Note: timestamps originate from collaboration sessions (RFM miner): window consists of multiple events in which a resource pair collaborated
    on a specific object at a certain point in time.
    The first time stamp was the earliest event, the last time stamp the last event, and the median indicates the median event in the window
    Here the events are of lesser importance and abstracted to only the start, end, and median timestamp of the window

    """
    def __init__(self,resource1, resource2, object, firstTimestamp, lastTimestamp, medianTimestamp):
        self.resource1 = resource1
        self.resource2 = resource2
        self.object = object
        self.firstTimestamp = firstTimestamp
        self.lastTimestamp = lastTimestamp
        self.medianTimestamp = medianTimestamp



    def getSource(self):
        return self.resource1

    def getTarget(self):
        return self.resource2

    def getTupleFormat(self):
        return (self.resource1,self.resource2)

    def getObject(self):
        return self.object

    def getFirstTimestamp(self):
        return self.firstTimestamp

    def getLastTimestamp(self):
        return self.lastTimestamp

    def getMedianTimestamp(self):
        return self.medianTimestamp



    def printTimes(self):
        print("Time: ", self.firstTimestamp.strftime("%d/%m/%Y, %H:%M:%S") , " -- ",  self.lastTimestamp.strftime("%d/%m/%Y, %H:%M:%S") )
