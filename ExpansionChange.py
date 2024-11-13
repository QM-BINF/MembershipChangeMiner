# Handle the membership change 'expansion'
import copy

import MembershipChange
import csv
import io

class ExpansionChange(MembershipChange.MembershipChange):

    def __init__(self):
        self.membershipChanges = []

    """
    Detect expansion membership change
    This is when a new member enters a group: increase group size and change network structure
    """
    def detectChanges(self,temporalGraph,expansionChangeMiner, expulsionChangeMiner):
        print("Detecting expansion changes")


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
    Search for expansion events between the teams 
    Add expansion events to self.membershipChanges
    @param previousGraph : Graph object representing the previous snapshot
    @param graph : Graph object representing the current snapshot 
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    """
    def compareSnapshots(self,previousGraph,graph, teamMatches):
        for match in teamMatches:
            oldTeam = match[0]
            newTeam = match[1]
            #if newTeam is not None: if it is None this means that all members have moved somewhere else or experienced turnover: never an expansion event, or an expansion event experienced in another group with nodes that originated from this group (is covered)

            if newTeam:
                if oldTeam:
                    intersect = set(oldTeam) & set(newTeam)
                    #new resources: new team with intersect resources removed
                    newMembers = newTeam.difference(intersect)

                    #For now: each new member is an expansion event
                    #Currently not implemented: subgroup expansion and other higher level events
                    for element in newMembers:
                        self.membershipChanges.append(dict({"timestamp":graph.getTimestamp(),"resource": element, "addedToGroup": oldTeam,"resultingGroup": newTeam ,"graphSnapshot": graph}))




                # if oldTeam is None: if newTeam is a single node, this is either expulsion or a new recruit; but if the newTeam exists of multiple nodes, this might be a expansion event
                #However we currently consider this as a reassignment event after recruitment
                else:
                    #if newTeam is a single node, do nothing
                    #else check
                    if len(newTeam) > 1:
                        #currently considered a reassignment event after recruitment
                        #if you wish to handle this in a different way, this is the place to edit
                        pass


    """
    Find if an expansion change took place between the timestamp and timestamp + timewindow of this resource   (the first in the window) 
    @param resource   resource ID 
    @param timestamp  datetime starting moment of the search 
    @param timewindow: timedelta indicating the ending point of the search 
    @return the the first expansion event in the window   or None
    """
    def findFirstExpansionChange(self, resource, beginTimestamp,  timewindow):
        expansionchanges = []
        endTimestamp = beginTimestamp + timewindow
        for change in self.membershipChanges:
            #starting from the timestamp <=  and <= timewindow : we include instantaneous changes
            if change["resource"] == resource and beginTimestamp <= change["timestamp"] and change["timestamp"] <= endTimestamp:
                expansionchanges.append(change)


        if expansionchanges:
            #sort them on timestamp and return the first
            expansionchanges.sort(key=lambda x: x["timestamp"])
            return expansionchanges[0]
        else:
            return None






    """
    Print out all expansion changes in the list 
    @param changes: list of  
    """
    def printDetectedChanges(self,changes):
        print("Expansion events:")
        for expansionChange in changes:
            print("At ", expansionChange["timestamp"]," resource ",expansionChange["resource"], " added to group ", expansionChange["addedToGroup"], " resulting in group ", expansionChange["resultingGroup"])

    """
        Print to CSV
        @param changes : list of expansion changes
         @param writer: writer pointer to open file
    """

    def printToCSV(self,  changes, writer):

        try:


            # write all the changes to the file
            for expansionChange in changes:
                writer.writerow([expansionChange["timestamp"], "Expansion","resource "+str(expansionChange["resource"])+
                                 " added to group "+str(expansionChange["addedToGroup"])+
                                 " resulting in group "+ str(expansionChange["resultingGroup"]) ])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')

    def printToCSVWithID(self, changes, writer):

        try:

            for expansionChange in changes:
                writer.writerow(
                    [expansionChange["timestamp"], "Expansion", str(expansionChange["resource"]), "resource " + str(expansionChange["resource"]) +
                     " added to group " + str(expansionChange["addedToGroup"]) +
                     " resulting in group " + str(expansionChange["resultingGroup"])])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')