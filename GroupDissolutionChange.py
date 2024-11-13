# Handle the membership change 'group dissolution'
import copy

import MembershipChange
import csv
import io


class GroupDissolutionChange(MembershipChange.MembershipChange):

    def __init__(self):
        self.membershipChanges = []

    """
    Detect group dissolution membership change
    This is when a group dissolves
    """

    def detectChanges(self, temporalGraph,expansionChangeMiner, expulsionChangeMiner):
        print("Detecting group dissolution changes")

        graphSnapshots = temporalGraph.getListOfGraphs()
        previousSnapshot = None
        for graph in graphSnapshots:

            if previousSnapshot:
                # compare wih the previous snapshot
                self.compareSnapshots(previousSnapshot, graph, temporalGraph.getGraphTeamMatches(graph))

            previousSnapshot = graph

        return self.membershipChanges

    """
    Compare the previous graph snapshot with the current 
    Search for group dissolution events between the teams 
    @param previousGraph : Graph object representing the previous snapshot
    @param graph : Graph object representing the current snapshot 
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    """

    def compareSnapshots(self, previousGraph, graph, teamMatches):
        for match in teamMatches:
            oldTeam = match[0]
            newTeam = match[1]

            if oldTeam:
                #there are still members: if there is only one original member left, we consider this group dissolution
                if newTeam:
                    intersect = oldTeam & newTeam
                    #there must be at least one member in common otherwise they wouldn't have been matched
                    if len(intersect) == 1 :
                        #could be group dissolution, if the old team had more than one member
                        if len(oldTeam) > 1:
                            #only one original member left, we consider this to be group dissolution
                            #optional: search in which teams the original members now reside
                            destinationTeams = self.getTeamsForResources(oldTeam, teamMatches)
                            self.membershipChanges.append(dict({"timestamp": graph.getTimestamp(), "originalGroup": oldTeam,
                                             "destinationTeams": destinationTeams}))

                else:
                    #newteam is None and the oldTeam was not a single resource
                    if len(oldTeam) > 1:
                        #team could be merged in its entirety: this is group merge NOT group dissolution !
                        #test if it is group merge
                        groupMerged = self.testGroupMerge(oldTeam,teamMatches)
                        if not groupMerged:
                            destinationTeams = self.getTeamsForResources(oldTeam, teamMatches)
                            self.membershipChanges.append(dict({"timestamp": graph.getTimestamp(), "originalGroup": oldTeam,
                                                            "destinationTeams": destinationTeams}))

    """
    Test if the team moved in its entirety to another team 
    @param team : set of resource IDs that make up a team 
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @return whether the team merged with another team 
    """

    def testGroupMerge(self,team, teamMatches):
        for teamMatch in teamMatches:
            if teamMatch[1] and team.issubset(teamMatch[1]):
                return True
        return False

    """
    Return the current teams where these resources reside in 
    @param resources: set of resource IDs
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @return list of sets that represent teams
    """
    def getTeamsForResources(self,resources,teamMatches):
        teams = []
        for element in resources:
            currentTeam = self.findCurrentTeam(element, teamMatches)
            if currentTeam and currentTeam not in teams:
                teams.append(currentTeam)
        return teams

    """
    Return the current team where this resource reside in 
    @param resources: a resource ID
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @return set that contains the resource ID or None if the resource has no current team
    """
    def findCurrentTeam(self, resourceID, teamMatches):
        for teams in teamMatches:
            if teams[1] and resourceID in teams[1]:
                return teams[1]
        return None




    """
    Print out all expansion changes in the list 
    @param changes: list of  
    """

    def printDetectedChanges(self, changes):
        print("Group dissolution events:")
        for change in changes:
            print("At ", change["timestamp"], " group ", change["originalGroup"], " dissolved, its members resulting in the following groups: ",
                  change["destinationTeams"])

    """
        Print to CSV
        @param changes : list of group dissolution changes
         @param writer: writer pointer to open file
        """

    def printToCSV(self, changes, writer):

        try:


            # write all the changes to the file
            for change in changes:
                writer.writerow([change["timestamp"], "Group Dissolution"," group "+ str(change["originalGroup"])+ " dissolved its members resulting in the following groups: "+str(change["destinationTeams"])])


        except Exception as e:
            #print('File does not exist. Please provide the correct CSV file name to write the changes to.')
            print(e)

    def printToCSVWithID(self, changes, writer):

        try:

            for change in changes:
                for member in change["originalGroup"]:
                    writer.writerow([change["timestamp"], "Group Dissolution",str(member), " group " + str(
                        change["originalGroup"]) + " dissolved its members resulting in the following groups: " + str(
                        change["destinationTeams"])])



        except Exception as e:
            # print('File does not exist. Please provide the correct CSV file name to write the changes to.')
            print(e)