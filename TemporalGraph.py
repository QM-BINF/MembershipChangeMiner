#a temporal graph consists of multiple Graph objects
#one for each time slice
import csv
import io

class TemporalGraph:

    """
    @param numberOfSlices: total number of graphs in this temporal graph, representing how many slices there are
    @param listOfGraphs: list of Graph objects ordered in time
    """
    def __init__(self,numberOfSlices,listOfGraphs):
    # unit for slicing of time in minutes
        self.timeSlice = 0
    # total number of time slices for which graphs exist == equals the length of the time_list_of_graphs
        self.numberOfGraphs = numberOfSlices
    #list of Graph objects, one for each time_slice
        self.timeListOfGraphs = listOfGraphs

    #dictionary with Graph object from listOfGraph as the key, and the team matches with the previous snapshot as the value
        self.graphTeamMatches = {}



    def getListOfGraphs(self):
        return self.timeListOfGraphs

    def getNumberOfGraphs(self):
        return self.numberOfGraphs

    """
    Append the teamMatches of this graph with its predecessor in the timeListOfGraphs to the dictionary 
    @param graph Graph object from the timeListOfGraphs
    @param teamMatches list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    Both represent the same group but some changes could have happened 
    """
    def appendGraphTeamMatch(self,graph, teamMatches):
        self.graphTeamMatches[graph] = teamMatches

    def getAllGraphTeamMatches(self):
        return self.graphTeamMatches

    def getGraphTeamMatches(self,currentSnapshot):
        return self.graphTeamMatches[currentSnapshot]

    """
    Get the maximum edge weight value 
    """
    def getMaxWeight(self):
        maxWeight = 0
        for g in self.timeListOfGraphs:
            w = g.getMaxEdgeWeight()
            if w > maxWeight:
                maxWeight = w
        return maxWeight




