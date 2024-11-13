

#class that represents an edge
class Edge:

    #@param source : Node object of source node
    #@param target: Node object of target node
    def __init__(self,source,target):
        self.sourceNode = source
        self.targetNode = target


        self.type = "Undirected"





    def getTupleFormat(self):
        return (self.sourceNode,self.targetNode)

    def getTupleFormatIDonly(self):
        return (self.sourceNode.getID(),self.targetNode.getID())



    def getSourceNode(self):
        return self.sourceNode

    def getSourceNodeID(self):
        return self.sourceNode.getID()

    def getTargetNode(self):
        return self.targetNode

    def getTargetNodeID(self):
        return self.targetNode.getID()

    def getType(self):
        return self.type

    #@param node: Node object
    #@returns boolean whether the node is part of this edge
    def containsNode(self,node):
        return ((self.sourceNode == node) or (self.targetNode == node))

    #check if the edge connects the 2 specified nodes
    def connects(self,node1,node2):
        return (((self.sourceNode == node1)and(self.targetNode == node2)) or ((self.sourceNode == node2)and(self.targetNode == node1)))


    def connectsResources(self,resource1, resource2):
        return (((self.sourceNode.getResource() == resource1)and(self.targetNode.getResource() == resource2)) or ((self.sourceNode.getResource() == resource2)and(self.targetNode.getResource() == resource1)))


