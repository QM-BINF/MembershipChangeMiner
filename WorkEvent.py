# a work event is a work session object transformed to an event: this means no duration , a single timestamp is chosen


class WorkEvent:

    def __init__(self,resource, timestamp ):
        self.resource = resource
        self.eventTimestamp = timestamp



    def getEventTimestamp(self):
        return self.eventTimestamp


    def getResource(self):
        return self.resource
