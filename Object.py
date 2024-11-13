
class Object:
    """
    @param ID: numerical ID of the object
    @param name: string label of object
    """
    def __init__(self,ID,name):
        self.name = name
        self.ID = ID



    def getLabel(self):
        return self.name

    def getID(self):
        return self.ID




