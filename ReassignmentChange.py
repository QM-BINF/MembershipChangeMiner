# Handle the membership change 'reassignment'
import copy

import MembershipChange
from datetime import datetime, timedelta
import sys
import csv
import io

class ReassingmentChange(MembershipChange.MembershipChange):

    def __init__(self):
        self.membershipChanges = []

    """
    Detect reassignment membership change
    This is when a member leaves a group to join another group 
    """
    def detectChanges(self,temporalGraph,expansionChangeMiner, expulsionChangeMiner):
        print("Detecting reassignment changes")
        graphSnapshots = temporalGraph.getListOfGraphs()

        self.findReassignmentChangesOverMultipleSnapshots(temporalGraph, graphSnapshots, expansionChangeMiner,
                                                         expulsionChangeMiner)
        return self.membershipChanges







    """
    Find the team from the previous snapshot that this resource originates from 
    @param resourceID  numerical ID of the resource 
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @return tuple from teamMatches where the previous snapshot contains this resource ID; None if the resource ID did not exist (a new recruit) 
    """
    def findOriginTeam(self,resourceID,teamMatches):
        for teams in teamMatches:
            #if origin team is not None
            if teams[0] and resourceID in teams[0]:
                return teams
        return None


    def findReassignmentChangesOverMultipleSnapshots(self,temporalGraph,graphSnapshots, expansionChangeMiner, expulsionChangeMiner):
        timewindow = timedelta(days = 3)
        #for each resource that has an expulsion change: search if they also have an expansion change within the timeframe
        expulsions = expulsionChangeMiner.getExpulsionChanges()
        for expulsion in expulsions:
            #search if an expansion change exist of this member in the timespan
            expansionChange = expansionChangeMiner.findFirstExpansionChange(expulsion["resource"], expulsion["timestamp"], timewindow)
            if expansionChange:
                #check eligibility and save if a reassignment change
                self.checkReassignmentEligibility(temporalGraph,graphSnapshots,expulsion,expansionChange)



    """
    Check if a reassignment took place for this expulsion change before (<=) the endTime 
    Explore all snapshots to track the evolution of this resource 
    @param graphSnapshots  list of Graph object indicating the evolution in the temporal graph 
    @param expulsionChange  dictionary with details on a singular expulsion change 
    @param expansionChange  dictionary with details on a singular expansion change 
    """
    def checkReassignmentEligibility(self,temporalGraph,graphSnapshots, expulsionChange, expansionChange):
        beginSnapshot = expulsionChange["graphSnapshot"]
        endSnapshot = expansionChange["graphSnapshot"]

        if beginSnapshot == endSnapshot:
            snapshots = [beginSnapshot]
        else:
            #first graph is the graph in which the expulsion happens, last one is the one where the expansion happens
            snapshots = self.getSnapshotsWithinRange(graphSnapshots,beginSnapshot, endSnapshot)

        #test instantaneous reassignment: if instantaneous there should be only one snapshot
        if len(snapshots) == 1:
            self.checkInstantaneousReassignment(temporalGraph,snapshots[0],expulsionChange["resource"])
        else:
            self.checkNonInstantaneousReassignment(temporalGraph,snapshots,expulsionChange["resource"],expulsionChange,expansionChange)







    """
    @param graphSnaphots : list of Graph items that are the sequential snapshots (ordered in time) 
    @param beginSnapshot : Graph object that is the first to include
    @param endSnapshot : Graph object that is the last to include
    @return list of graph snapshots that begins with the first Graph object and ends with the last Graph object
    """
    def getSnapshotsWithinRange(self,graphSnapshots,beginSnapshot, endSnapshot):
        inRange = []
        include = False
        for graph in graphSnapshots:
            if graph == beginSnapshot:
                include = True

            if include :
                inRange.append(graph)

            if graph == endSnapshot:
                include = False
                break

        return inRange




    """
    Check instantaneous reassignment : there is only one snapshot: if a reassignment change: add to the membership dictionary
    @param temporalGraph : TemporalGraph object representing the temporal graph
    @param snapshots list of Graph objects ordered in time : first snapshot is when the expulsion change happens
                    the last snapshot is when the expansion change happens 
    @param resource  : resource ID that experienced reassignment change
    """
    def checkInstantaneousReassignment(self, temporalGraph, snapshot,resource):
        #get the team matches
        matches = temporalGraph.getGraphTeamMatches(snapshot)
        expulsionTuple = self.findExpulsionTuple(matches, resource)
        expansionTuple = self.findExpansionTuple(matches, resource)

        # Checks
        originTeamPrevious = expulsionTuple[0]
        originTeamCurrent = expulsionTuple[1]
        destinationTeamPrevious = expansionTuple[0]
        destinationTeamCurrent = expansionTuple[1]
        # resource should not be the only resource in its origin group : normally covered by expulsion

        if len(originTeamPrevious) > 1:  #this test is probably not necessary as it is covered by expulsion change
            # check group merge
            if not originTeamCurrent:
                # entire team is gone: check if they merged with this group: originteam is completely moved to newteam : add NOT
                # if not completely in this new team, then the old members are spread out over different teams and this is still reassignment change
                if originTeamPrevious.difference(destinationTeamCurrent):
                    # add reassignment change
                    self.membershipChanges.append(dict(
                        {"timestamp": snapshot.getTimestamp(), "resource": resource, "reassignedFrom": originTeamPrevious,
                         "reassignedTo": destinationTeamCurrent, "resultingOriginGroup": originTeamCurrent,
                         "originalDestinationGroup": destinationTeamPrevious}))
            # after reassignment the origin team is not empty
            else:
                # Currently subgroup reassignment is not supported: this would be the place to check for it
                self.membershipChanges.append(dict(
                    {"timestamp": snapshot.getTimestamp(), "resource": resource,
                     "reassignedFrom": originTeamPrevious, "reassignedTo": destinationTeamCurrent,
                     "resultingOriginGroup": originTeamCurrent, "originalDestinationGroup": destinationTeamPrevious}))

    """
        Check non instantaneous reassignment : there are multiple snapshots 
        @param temporalGraph : TemporalGraph object representing the temporal graph
        @param snapshots list of Graph objects ordered in time : first snapshot is when the expulsion change happens
                        the last snapshot is when the expansion change happens 
        @param resource  : resource ID that experienced reassignment change
    """
    def checkNonInstantaneousReassignment(self,temporalGraph,snapshots,resource,expulsionChange,expansionChange):
        #None -> {x}  first snapshot
        #{x}  -> {x}  (possibly multiple times)
        #{x} -> {None}  (must be different team than origin team)  last snapshot
        originTeam = None
        numberOfSnapshots = len(snapshots)

        for i in range(0, numberOfSnapshots):
            matches = temporalGraph.getGraphTeamMatches(snapshots[i])
            if i == 0: #first snapshot

                originTeam = expulsionChange["resultingGroup"]
                destinationMatch = self.findDestinationTeam(matches,resource)
                if not destinationMatch:
                    break
                #None -> {x}  if not break the loop, no reassignment change here
                if not (not destinationMatch[0] and destinationMatch[1] == {resource}):
                    break
            #last snapshot: {x} --> None and destination team must not be the same as originTeam
            elif i == (numberOfSnapshots-1):
                destinationTeam = expansionChange["addedToGroup"]
                expansionMatch = self.findOriginTeam(resource,matches)
                if not expansionMatch:
                    break
                # {x} -> None
                if not (expansionMatch[0] == {resource} and not expansionMatch[1]):
                    break
                #reassignment cannot be to the origin team, must be a different team the member is reassigned to
                elif originTeam == destinationTeam :
                    break
                else:
                    #add as reassignment change  : timestamp is a range now
                    self.membershipChanges.append(dict(
                        {"timestamp": ""+expulsionChange["timestamp"].strftime("%Y-%m-%d, %H:%M:%S")+" - "+ expansionChange["timestamp"].strftime("%Y-%m-%d, %H:%M:%S"), "resource": resource,
                         "reassignedFrom": expulsionChange["removedFromGroup"], "reassignedTo": expansionChange["resultingGroup"],
                         "resultingOriginGroup": expulsionChange["resultingGroup"],
                         "originalDestinationGroup": expansionChange["addedToGroup"]}))
            else:
                #{x} -> {x} and keep track of the origin team
                stable = self.trackExpulsionStability(matches, resource)
                if not stable:
                    break
                #else the resource is stable: track evolution of its origin group

                originTeam = self.trackEvolutionOfGroup(originTeam, matches)
                #if the originTeam disappears, this is dissolution, and not reassignment
                if not originTeam:
                    break



    """
    Keep track of this team and what it becomes
    """
    def trackEvolutionOfGroup(self,team, matches ):
        for match in matches:
            if match[0] == team:
                return match[1]

    """
    Track whether {resource} -> {resource}  is in the list of matches
    @param matches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @param resource : resource ID 
    @return True if it exists in the list or False if it doesn't
    """
    def trackExpulsionStability(self,matches, resource):
        tuple = ({resource},{resource})
        return tuple in matches



    """
    Search the match combination in which resource is present in the current team
    @param matches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @param resource : resource ID 
    @return match tuple where resource ID is in the second element of the tuple   or None 
    """
    def findDestinationTeam(self,matches, resource):
        for match in matches:
            if resource in match[1]:
                return match
        return None

    """
    Team the resource belongs to in the previous snapshot
    @param matches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @param resource : resource ID 
    @return match tuple where resource ID is in the first element of the tuple 
    """
    def findExpulsionTuple(self, matches, resource):
        for match in matches:
            previous = match[0]
            if resource in previous:
                return match
        #there should be a match
        sys.exit("Resource ",resource, "  should exist in graph snapshot but does not.")

    """
    Team the resource belongs to in the current snapshot
    @param matches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @param resource : resource ID 
    @return match tuple where resource ID is in the second element of the tuple 
    """

    def findExpansionTuple(self, matches, resource):
        for match in matches:
            current = match[1]
            if resource in current:
                return match
                # there should be a match
        sys.exit("Resource ", resource, "  should exist in graph snapshot but does not.")


    """
    Print out all expansion changes in the list 
    @param changes: list of  
    """
    def printDetectedChanges(self,changes):
        print("Reassignment events:")
        for change in changes:
            print("At ", change["timestamp"]," resource ",change["resource"], " reassigned from group ", change["reassignedFrom"], " to group ", change["originalDestinationGroup"], " resulting in ", change["reassignedTo"])

    """
    Print to CSV
    @param changes : list of reassignment changes
     @param writer: writer pointer to open file
    """
    def printToCSV(self,  changes, writer):

        try:

            # write all the changes to the file
            for change in changes:
                writer.writerow([change["timestamp"], "Reassignment", str(change["resource"]) + " reassigned from group "+ str(change["reassignedFrom"])+" to group "+ str(change["originalDestinationGroup"])+ " resulting in "+ str(change["reassignedTo"])])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')


    def printToCSVWithID(self,  changes, writer):

        try:

            # write all the changes to the file
            for change in changes:
                writer.writerow([change["timestamp"], "Reassignment", str(change["resource"]), str(change["resource"]) + " reassigned from group "+ str(change["reassignedFrom"])+" to group "+ str(change["originalDestinationGroup"])+ " resulting in "+ str(change["reassignedTo"])])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')