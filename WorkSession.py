#class that represents a work session object


class WorkSession:

    """
    @param resource: Resource object representing the resource
    @param firstTimestamp: date time object indicating the beginning of the window
    @param lastTimestamp: date time object indicating the end of the window
    @param medianTimestamp: date time object indicating the median timestamp in the window
    Note: timestamps originate from work sessions (RFM miner): window consists of multiple events in which a resource
    worked on any objects at a certain point in time.
    The first time stamp was the earliest event, the last time stamp the last event, and the median indicates the median event in the window
    Here the events are of lesser importance and abstracted to only the start, end, and median timestamp of the window

    """
    def __init__(self,resource, firstTimestamp, lastTimestamp, medianTimestamp):
        self.resource = resource

        self.firstTimestamp = firstTimestamp
        self.lastTimestamp = lastTimestamp
        self.medianTimestamp = medianTimestamp



    def getResource(self):
        return self.resource



    def getFirstTimestamp(self):
        return self.firstTimestamp

    def getLastTimestamp(self):
        return self.lastTimestamp

    def getMedianTimestamp(self):
        return self.medianTimestamp



    def printTimes(self):
        print("Time: ", self.firstTimestamp.strftime("%d/%m/%Y, %H:%M:%S") , " -- ",  self.lastTimestamp.strftime("%d/%m/%Y, %H:%M:%S") )
