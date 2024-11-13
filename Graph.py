import Edge
import TieStrengthHandler
import Node
import sys
import networkx as nx

class Graph:

    """
    @param nodes:  list of Node objects that will be the nodes of the graph
    @param edges: list of Edge objects that will be the edges
    @param edgeWeights  dict with as key the edge object and value the weight
    """
    def __init__(self,nodes = [],edges = [],edgeWeights = {},currentWeightsTimestamp = None):
        #nodes
        self.nodes = nodes
        #edges
        self.edges = edges
        #edge weight is graph snapshot dependent
        self.edgeWeights = edgeWeights
        self.currentWeightsTimestamp = currentWeightsTimestamp

        #These variables are set when teams are being detected
        #networkx graph representing this graph
        self.netwxGraph = None
        #teams of nodes
        self.teams = None


    """
    @return copy of this Graph object that isn't linked to this Graph object anymore, except for the Node and Edge object in the nodes and edges lists
    """
    def deepCopy(self):
        #new list with same edge and nodes objects (these are still linked to this Graph object!)
        nodes = []
        for n in self.nodes:
            nodes.append(n)
        edges = []
        for e in self.edges:
            edges.append(e)

        #medium deep copy of edgeweights : new dict, but linked Edge objects as keys
        edgeWeights = {}
        for e,w in self.edgeWeights.items():
            edgeWeights[e] = w

        #deep copy of weights timestamp is not necessary, this is an immutable object

        copyGraph = Graph(nodes,edges,edgeWeights,self.currentWeightsTimestamp)
        return copyGraph

    def getListOfNodeIDs(self):
        nodeIDs = [target.getID() for target in self.nodes]
        return nodeIDs

    def getEdges(self):
        return self.edges

    def numberOfNodes(self):
        return len(self.nodes)
    def getMaxEdgeWeight(self):
        #Problem if there are no edges : return 0
        if not self.edgeWeights.values() :
            return 0
        else:
            return max(self.edgeWeights.values())

    """
    @return list of 3 tuples of edges (u,v,w) with u source ID, v target ID and w the edge weight 
    """
    def getListOfEdges(self):
        edgesList = []
        for e in self.edges:
            edgeIDs = e.getTupleFormatIDonly()
            edgesList.append((edgeIDs[0],edgeIDs[1],self.edgeWeights[e]))

        return edgesList

    """
    @param resourceID  resourceID that is a node in this graph
    @return list of resourceIDs that are neighbors of this resource 
    """
    def getNeighborIDs(self,resourceID):
        neighbors = []
        for edge in self.edges:
            edgeIDs = edge.getTupleFormatIDonly()
            if edgeIDs[0] == resourceID:
                neighbors.append(edgeIDs[1])
            elif edgeIDs[1] == resourceID:
                neighbors.append(edgeIDs[0])
        return neighbors


    def getNetworkxGraph(self):
        return self.netwxGraph

    def setCurrentWeightsTimestamp(self,timestamp):
        self.currentWeightsTimestamp = timestamp



    def getCurrentWeightsTimestamp(self):
        return self.currentWeightsTimestamp

    def getTimestamp(self):
        return self.currentWeightsTimestamp

    """
    @param teams: dict with node ID as key and community number as value
    """
    def setTeams(self,teams):
        self.teams = teams

    """
    @return dict with the NodeID as key and community number as value
    """
    def getTeams(self):
        return self.teams
    """
    @param resourcesList: list of resource objects that will become nodes
    """
    def addResourcesAsNodes(self, resourcesList):
        for resource in resourcesList:
            self.addNode(Node.Node(resource))

    """
    Add node object to nodes list 
    @param node: Node object representing a resource
    """
    def addNode(self,node):
        if node not in self.nodes:
            self.nodes.append(node)



    """
    Create a new Edge object between these two resources, and add new weight to dictionary 
    Nodes for the involved resources should exist already 
    @param resource: resource object 
    @param tieStrengthHandler: object of this class that holds all mechanisms of tie decay and evolution 
    @return the new Edge object 
    """
    def createNewEdge(self,resource1,resource2,tieStrengthHandler):
        #find node objects: they should exist already
        node1 = self.findNode(resource1)
        if node1 is None:
            sys.exit("Node ", node1.getLabel(), "  should exist already but does not.")

        node2 = self.findNode(resource2)
        if node2 is None:
            sys.exit("Node ", node2.getLabel(), "  should exist already but does not.")


        newEdge = Edge.Edge(node1,node2)
        self.edges.append(newEdge)
        #set the edge weight
        #add new edge to dictionary
        strength = tieStrengthHandler.handleInteraction(0)
        self.edgeWeights[newEdge] = strength
        return newEdge

    #Remove this edge
    def removeEdge(self,edge):
        #remove from edgelist
        self.edges.remove(edge)
        #remove from edge weights dict
        del self.edgeWeights[edge]


    """
    Create a new Node object 
    @param resource: Resource object that the node represents
    """
    def createNewNode(self,resource):
        newNode = Node.Node(resource)
        self.nodes.append(newNode)
        return newNode
    """
    Find Node object that represents this resource 
    @param Resource object 
    @return the Node object or None if no node exists 
    """
    def findNode(self,resource):
        node = [target for target in self.nodes if target.getResource()==resource]
        if not node:
            node = None
        else:
            node = node[0]
        return node

    """
    Find edge between these two resources 
    @param resource:  Resource object 
    @return either the edge between the resources or None if no such edge exists
    """
    def findEdge(self, resource1, resource2):
        edges = [target for target in self.edges if target.connectsResources(resource1,resource2)]
        #should only return 0 or 1  edge
        if not edges:
            edges = None
        else:
            edges = edges[0]
        return edges

    """
    Find the weight of the edge 
    @param edge Edge object to find the weight for in the dictionary 
    @returns  the weight value of the edge arg
    """
    def findEdgeWeight(self,edge):
        return self.edgeWeights[edge]

    """
    @param edge: edge object to set the new weight for
    @param weight: new weight for edge object
    """
    def setEdgeWeight(self,edge,weight):
        self.edgeWeights[edge] = weight

    """
    Increase the tie strength of the resources of these collaboration events with the jump size 
    Update also the dictionary that keeps track of when the last event on an edge took place 
    @param interactions: list of CollaborationEvent objects all happening at the same timestamp 
    @param tieStrengthHandler: object of this class that holds all mechanisms of tie decay and evolution 
    @param lastEventOnEdge : dictionary with Edge object as key and the timestamp of the last event on this edge and its weight at that point as values
    @param currentTS  timestamp of current snapshot at which the interactions take place 
    """
    def handleInteractions(self, interactions,tieStrengthHandler, lastEventOnEdge, currentTS):
        for ce in interactions:
            #find which resources this collab event is between
            resource1, resource2 = ce.getTupleFormat()

            #There could be an edge or no edge !

            #find their current edge tie strength value
            edge = self.findEdge(resource1,resource2)
            #if there does not exist an edge, create one
            if edge is None:
                #this already sets the strength as well
                edge = self.createNewEdge(resource1,resource2,tieStrengthHandler)

            #there exists an edge, gets its current strength and increase it
            else:
                #find edge weight
                currentStrengthValue = self.findEdgeWeight(edge)
                #increase their tie strength
                newStrengthValue = tieStrengthHandler.handleInteraction(currentStrengthValue)
                #set the new edge weight
                self.setEdgeWeight(edge,newStrengthValue)

            #update this in the last event on edge dictionary
            lastEventOnEdge[edge] = (currentTS,self.findEdgeWeight(edge))


    """
    Handle the decay of edges 
    Need to know: 
            - previous weight at the last event
            - time steps between the time of the last event on the edge and the new time we wish to calculate 
    @param tieStrengthHandler: object of this class that holds all mechanisms of tie decay and evolution 
    @param targetTimestamp: timestamp we wish to calculate the new edge weight for  
    @param lastEventOnEdge: dictionary with Edge object as key and the timestamp of the last event on this edge and its weight at that point as values
    @return a list of Edge objects that are removed from the graph 
    """
    def decayEdges(self,tieStrengthHandler,targetTimestamp,lastEventOnEdge):
        removedEdges = []

        #decay each edge
        for edge in self.edges:

            #get timestamp of last event on this edge and the weight of the edge at that point
            lastEventTS, lastEventWeight = lastEventOnEdge[edge]
            #get number of time steps between the timestamp of last event and current timestamp
            numberOfTimeSteps = tieStrengthHandler.calculateNumberOfTimeSteps(lastEventTS, targetTimestamp)

            #calculate new weight
            newWeight = tieStrengthHandler.decayEdgeWeight(lastEventWeight,numberOfTimeSteps)
            #set new weight
            self.setEdgeWeight(edge,newWeight)

            #handle cutoff threshold : we choose < as if there is still an event at this timestamp, the edge weight increases by jump size instead of starting from 0
            # interpretation: only strict after the given period of decay the edge disappears
            if newWeight < tieStrengthHandler.getWeightCutoffThreshold():
                #edge disappears
                self.removeEdge(edge)
                removedEdges.append(edge)
                #remove also from last event on edge
                del lastEventOnEdge[edge]

        return removedEdges




    """
    Handle all node events: for now only the appearance of new nodes in the graph
    @param listOfPopupResources: list of Resource objects that are new to the temporal graph and should be added as nodes
    """
    def handleNodeEvents(self,listOfPopupResources):
        #Handle new nodes
        for resource in listOfPopupResources:
            self.createNewNode(resource)

    """
       Create a networkx graph for the graph  
       @return networkx Graph object that represents the graph 
       """

    def createNetworkxGraph(self):
        # get list of nodes
        nodes = self.getListOfNodeIDs()

        # get list of edges with weights
        edges = self.getListOfEdges()
        netwxGraph = nx.Graph()
        netwxGraph.add_nodes_from(nodes)
        netwxGraph.add_weighted_edges_from(edges)

        self.netwxGraph = netwxGraph

        return netwxGraph