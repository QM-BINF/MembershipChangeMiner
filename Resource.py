#class that represents a resources


class Resource:

    """
    @param id  numerical id of resource
    @param name  string label of resource
    """
    def __init__(self,id,name):
        self.name = name
        self.ID = id

        #list of all the collaboration sessions this resource is involved in
        self.collabs = []
        #list of all the work sessions this resource is involved in
        self.works = []



    def getLabel(self):
        return self.name

    def setName(self,name):
        self.name = name

    def getID(self):
        return self.ID



    def getCollabSessions(self):
        return self.collabs

    """
    #Append this collab session to the resource's list of collab sessions in which they are involved
    #@param collabSession  : CollaborationSession object
    """
    def addCollabSession(self,collab):
        self.collabs.append(collab)


    """
    Append the work session to the resource's list of work sessions in which they are involved
    @param session: WorkSession object
    """
    def addWorkSession(self,session):
        self.works.append(session)


