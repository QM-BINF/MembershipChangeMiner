
# Handle the membership change 'group partition'


import MembershipChange
import csv
import io

class GroupPartitionChange(MembershipChange.MembershipChange):

    def __init__(self):
        self.membershipChanges = []

    """
    Detect group partition membership change
    This is when a group splits into multiple subgroups 
    """

    def detectChanges(self, temporalGraph,expansionChangeMiner, expulsionChangeMiner):
        print("Detecting group partition changes")

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
    Search for group partition events between the teams 
    @param previousGraph : Graph object representing the previous snapshot
    @param graph : Graph object representing the current snapshot 
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    """

    def compareSnapshots(self, previousGraph, graph, teamMatches):
        for match in teamMatches:
            oldTeam = match[0]
            newTeam = match[1]

            if newTeam:
                #the team did previously not exist and it is not a single member because that would be expulsion
                 if not oldTeam and len(newTeam) > 1:
                    #look if this is a partition of an original team
                    partedGroup,originalTeam = self.testGroupPartition(newTeam, teamMatches)
                    if originalTeam:

                        # Currently there is a restriction on only PURE splits meaning each part of the original group is a seperate group without new expansions etc.
                        self.membershipChanges.append(dict({"timestamp": graph.getTimestamp(), "originalGroup": originalTeam,
                                                            "splitInto": partedGroup}))








    """
   
    @param team set of resource IDs that make up a team 
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @return the different parts of the team that has split, and the original team that has split; OR None, None if it is not a clean partition change
    """

    def testGroupPartition(self,team, teamMatches):
        teamParts = []
        #team together with some other new teams consistute an old team
        originalTeam = self.findOriginalTeam(team, teamMatches)

        if originalTeam:


            teamParts.append(team)

            #get which resources we still need to find
            remainingResources = originalTeam.difference(team)
            while remainingResources:
                partitionPart, remainingResources= self.findTeam(remainingResources,teamMatches)
                if partitionPart:
                    teamParts.append(partitionPart)
                else:
                    #not a clean split, this is no pure partition change
                    return None, None


        return teamParts,originalTeam

    """

    @param team set of resource IDs that make up a team 
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @return the oldTeam of which team was a part or None if they were not part of a single group 
    """
    def findOriginalTeam(self,team,teamMatches):
        for teamMatch in teamMatches:
            if teamMatch[0] :
                if team.issubset(teamMatch[0]):
                    return teamMatch[0]
        return None

    """
    Find the new team of these resources 
    @param resources set of resource IDs
    @param teamMatches list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @return the new team which (some of ) the resources are now part of and the set of remaining resources that are not part of this new team (need to iterate again)
    if all resources are found, the method returns the team, and an empty set 
    if not all resources can be found, the method returns None, None 
    """
    def findTeam(self,resources, teamMatches):
        for teamMatch in teamMatches:
            if teamMatch[1]:
                if teamMatch[1].issubset(resources):
                    remainingResources = resources.difference(teamMatch[1])
                    return teamMatch[1], remainingResources

        return None, None

    """
    Print out all expansion changes in the list 
    @param changes: list of  
    """

    def printDetectedChanges(self, changes):
        print("Group partition events:")
        for change in changes:
            print("At ", change["timestamp"], " group ", change["originalGroup"], " parted into subgroups ",
                  change["splitInto"])

    """
    Print to CSV
    @param changes : list of grou partition changes
    @param writer: writer pointer to open file
    """

    def printToCSV(self, changes, writer):

        try:

            # write all the changes to the file
            for change in changes:
                writer.writerow([change["timestamp"], "Group Partition"," group "+ str(change["originalGroup"])+ " parted into subgroups "+
                  str(change["splitInto"])])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')



    def printToCSVWithID(self, changes, writer):

        try:

            for change in changes:
                for member in change["originalGroup"]:
                    writer.writerow([change["timestamp"], "Group Partition",str(member), " group "+ str(change["originalGroup"])+ " parted into subgroups "+
                  str(change["splitInto"])])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')