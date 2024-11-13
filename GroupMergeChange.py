# Handle the membership change 'group merge'


import MembershipChange
import csv
import io


class GroupMergeChange(MembershipChange.MembershipChange):

    def __init__(self):
        self.membershipChanges = []

    """
    Detect group merge membership change
    This is when 2 groups merge 
    """

    def detectChanges(self, temporalGraph,expansionChangeMiner, expulsionChangeMiner):
        print("Detecting group merge changes")

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
    Search for group merge events between the teams 
    @param previousGraph : Graph object representing the previous snapshot
    @param graph : Graph object representing the current snapshot 
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    """

    def compareSnapshots(self, previousGraph, graph, teamMatches):
        for match in teamMatches:
            oldTeam = match[0]
            newTeam = match[1]

            if oldTeam:
                #is the old team completely merged into another team? (and old team did not exist of a single resource because this would be expansion)
                if not newTeam and len(oldTeam) > 1:
                    #look if the team in its entirety got merged to another team
                    mergedGroup = self.testGroupMerge(oldTeam, teamMatches)
                    if mergedGroup:
                        #the team is incorporated into another team (newTeam)
                        #can oldTeam be None? No since it then would have matched with the team that is merged
                        #currently there is the restriction that the group with who the team merged must also still be in its entirety
                        if mergedGroup[0] and mergedGroup[0].issubset(mergedGroup[1]):
                            self.membershipChanges.append(dict({"timestamp": graph.getTimestamp(), "originalGroup": oldTeam,
                                                            "mergedWith": mergedGroup[0],"resultingGroup":mergedGroup[1]}))







    """
    Test if the team moved in its entirety to another team 
    @param team set of resource IDs that make up a team 
    @param teamMatches:  list of tuples containing a set of nodes that form a group in the previous snapshot, and a set of node IDs that form a group in this graph 
    @return the teamMatch of which the newTeam contains the team param, or None if the team was not merged to another team in its entirety
    """

    def testGroupMerge(self,team, teamMatches):
        for teamMatch in teamMatches:
            if teamMatch[1] and team.issubset(teamMatch[1]):
                return teamMatch
        return None




    """
    Print out all expansion changes in the list 
    @param changes: list of  
    """

    def printDetectedChanges(self, changes):
        print("Group merge events:")
        for change in changes:
            print("At ", change["timestamp"], " group ", change["originalGroup"], " merged with ",
                  change["mergedWith"], " resulting in group ", change["resultingGroup"])

    """
    Print to CSV
    @param changes : list of group merge changes
    @param writer: writer pointer to open file
    """

    def printToCSV(self,  changes, writer):

        try:


            # write all the changes to the file
            for change in changes:
                writer.writerow([change["timestamp"], "Group Merge",
                                 " group " + str(change["originalGroup"]) + " merged with "+
                  str(change["mergedWith"])+ " resulting in group "+ str(change["resultingGroup"])])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')

    def printToCSVWithID(self, changes, writer):

        try:

            for change in changes:
                for member in change["originalGroup"]:
                    writer.writerow([change["timestamp"], "Group Merge", str(member),
                                 " group " + str(change["originalGroup"]) + " merged with " +
                                 str(change["mergedWith"]) + " resulting in group " + str(change["resultingGroup"])])
                for member in change["mergedWith"]:
                    writer.writerow([change["timestamp"], "Group Merge", str(member),
                                     " group " + str(change["originalGroup"]) + " merged with " +
                                     str(change["mergedWith"]) + " resulting in group " + str(
                                         change["resultingGroup"])])

        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')