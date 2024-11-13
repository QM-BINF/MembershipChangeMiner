#Monitor the snapshots for membership changes

import MembershipChange
import RecruitmentChange
import ExpansionChange
import TeamMatcher
import ExpulsionChange
import ReassignmentChange
import GroupDissolutionChange
import GroupMergeChange
import GroupPartitionChange
import csv
import io

class MembershipChangeMonitor:

    """
    @param temporalGraph an object of class TemporalGraph that represents a temporal graph with different snapshots
    """
    def __init__(self, temporalGraph):
        self.temporalGraph = temporalGraph
        self.expansionChangeMiner = None
        self.expulsionChangeMiner = None

        #match teams between snapshots
        self.matchTeams()


        #dictionary with membership changes: type of change is key, value is another dictionary with the relevant details
        self.membershipChanges = {}
        self.enableChanges()




    """
    Enable which changes must be detected : for each type of change make an object and add it to the membershipChanges dict
    """
    def enableChanges(self):
        #recruitment
        recruitmentChangeMiner = RecruitmentChange.RecruitmentChange()
        self.membershipChanges[recruitmentChangeMiner] = None
        expansionChangeMiner = ExpansionChange.ExpansionChange()
        self.expansionChangeMiner = expansionChangeMiner
        self.membershipChanges[expansionChangeMiner] = None
        expulsionChangeMiner = ExpulsionChange.ExpulsionChange()
        self.expulsionChangeMiner = expulsionChangeMiner
        self.membershipChanges[expulsionChangeMiner] = None
        reassignmentChangeMiner = ReassignmentChange.ReassingmentChange()
        self.membershipChanges[reassignmentChangeMiner] = None
        groupDissolutionChangeMiner = GroupDissolutionChange.GroupDissolutionChange()
        self.membershipChanges[groupDissolutionChangeMiner] = None
        groupMergeChangeMiner = GroupMergeChange.GroupMergeChange()
        self.membershipChanges[groupMergeChangeMiner] = None
        groupPartitionChangeMiner = GroupPartitionChange.GroupPartitionChange()
        self.membershipChanges[groupPartitionChangeMiner] = None


    """
    
    """
    def detectMembershipChanges(self):
        #detect all enabled changes
        for key in self.membershipChanges:
            #some changes build upon the expansion and expulsion changes already found
            detectedChanges = key.detectChanges(self.temporalGraph, self.expansionChangeMiner, self.expulsionChangeMiner)
            self.membershipChanges[key] = detectedChanges


    """
    Print all the detected changes in the console 
    """
    def printDetectedMembershipChanges(self):
        for typeOfChange, listOfChanges in self.membershipChanges.items():
            typeOfChange.printDetectedChanges(listOfChanges)

    """
    Print all the detected changes to CSV file
    """
    def printDetectedChangesToCSV(self, filename):
        #clear file
        writer = csv.writer(io.open(filename, 'w+', newline='', encoding="utf-8"), delimiter=";")
        # write the header: Date, change type, details
        writer.writerow(["Timestamp", "Change type", "Details"])
        for typeOfChange, listOfChanges in self.membershipChanges.items():
            typeOfChange.printToCSV(listOfChanges, writer)

    def printDetectedChangesToCSVWithResourceID(self, filename):
        # clear file
        writer = csv.writer(io.open(filename, 'w+', newline='', encoding="utf-8"), delimiter=";")
        # write the header: Date, change type, details
        writer.writerow(["Timestamp", "Change type", "Resource ID", "Details"])
        for typeOfChange, listOfChanges in self.membershipChanges.items():
            typeOfChange.printToCSVWithID(listOfChanges, writer)

    def matchTeams(self):
        graphSnapshots = self.temporalGraph.getListOfGraphs()
        previousSnapshot = None
        for graph in graphSnapshots:

            if previousSnapshot:
                # compare wih the previous snapshot to match the teams
                teamMatches = TeamMatcher.matchTeamsBetweenSnapshots(previousSnapshot, graph)
                #add to the temporal graph
                self.temporalGraph.appendGraphTeamMatch(graph,teamMatches)

            previousSnapshot = graph




