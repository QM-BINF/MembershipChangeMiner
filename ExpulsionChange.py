# Handle the membership change 'expansion'
import copy

import MembershipChange
import csv
import io

class ExpulsionChange(MembershipChange.MembershipChange):

    def __init__(self):
        self.membershipChanges = []

    """
    Detect expulsion membership change
    This is when a member leaves a group: decrease group size and changed network structure
    """
    def detectChanges(self,temporalGraph,expansionChangeMiner, expulsionChangeMiner):
        print("Detecting expulsion changes")


        graphSnapshots = temporalGraph.getListOfGraphs()
        previousSnapshot = None
        for graph in graphSnapshots:

            if previousSnapshot:
                #compare wih the previous snapshot
                self.compareSnapshots(previousSnapshot,graph,temporalGraph.getGraphTeamMatches(graph))

            previousSnapshot = graph



        return self.membershipChanges


    """
    Compare the previous graph snapshot with the current 
    Search for expulsion events between the teams 
    @param previousGraph : Graph object representing the previous snapshot
    @param graph : Graph object representing the current snapshot 
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    """
    def compareSnapshots(self,previousGraph,graph, teamMatches):
        for match in teamMatches:
            oldTeam = match[0]
            newTeam = match[1]
           #if oldTeam is None, this can never be expulsion, so don't worry about it
            if oldTeam:
                if newTeam:
                    exMembers = oldTeam.difference(newTeam)
                    #For now: each new member is an expulsion event
                    #Currently not implemented: subgroup expulsion and other higher level events

                    for element in exMembers:
                        self.membershipChanges.append(dict({"timestamp":graph.getTimestamp(),"resource": element, "removedFromGroup": oldTeam,"resultingGroup": newTeam , "graphSnapshot": graph}))








    """
    Print out all expansion changes in the list 
    @param changes: list of  
    """
    def printDetectedChanges(self,changes):
        print("Expulsion events:")
        for expulsionChange in changes:
            print("At ", expulsionChange["timestamp"]," resource ",expulsionChange["resource"], " removed from group ", expulsionChange["removedFromGroup"], " resulting in group ", expulsionChange["resultingGroup"])



    """
    Get which resource IDS experienced expulsion and the timestamp when this happened 
    @return list of dictionary with each entry a dict with timestamp , resource, removedFromGroup, and resultingGroup  
    """
    def getExpulsionChanges(self):
       return self.membershipChanges

    """
            Print to CSV
            @param changes : list of expulsion changes
            @param writer: writer pointer to open file
        """

    def printToCSV(self,  changes, writer):

        try:


            # write all the changes to the file
            for change in changes:
                writer.writerow([change["timestamp"], "Expulsion", " resource "+str(change["resource"]) +" removed from group "+ str(change["removedFromGroup"])+ " resulting in group "+ str(change["resultingGroup"])])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')



    def printToCSVWithID(self,  changes, writer):

        try:

            for change in changes:
                writer.writerow([change["timestamp"], "Expulsion",str(change["resource"]), " resource "+str(change["resource"]) +" removed from group "+ str(change["removedFromGroup"])+ " resulting in group "+ str(change["resultingGroup"])])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')