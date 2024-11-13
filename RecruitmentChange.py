# Handle the membership change 'recruitment'
import MembershipChange
import csv
import io

class RecruitmentChange(MembershipChange.MembershipChange):

    def __init__(self):
        self.membershipChanges = {}

    """
    Detect recruitment membership change
    This is when a new member appears in the population
    returns dict of all recruitment changes
    """
    def detectChanges(self,temporalGraph, expansionChangeMiner, expulsionChangeMiner):
        print("Detecting recruitment changes")
        #NodeID and timestamp
        membershipChanges = {}
        graphSnapshots = temporalGraph.getListOfGraphs()
        previousSnapshot = None
        for graph in graphSnapshots:
            #if a new node ID appears between two snapshots, a recruitment event took place
            if previousSnapshot:
                #compare wih the previous snapshot
                previousNodes = previousSnapshot.getListOfNodeIDs()
                currentNodes = graph.getListOfNodeIDs()
                newNodes = [el for el in currentNodes if el not in previousNodes]
                #make for each recruitment a change event
                for newNode in newNodes:
                    membershipChanges[newNode] = graph.getTimestamp()

            #########else:  first snapshot: all nodes are considered to be 'new'
            #but since we don't often start at the beginning but somewhere in the middle of the dataset,
            #we do not consider this first snapshot to contain any changes
            #if you do wish to add these nodes as recruitments, uncommon the following lines

            #else:
            #    currentNodes = graph.getListOfNodeIDs()
            #    for node in currentNodes:
            #        membershipChanges[node] = graph.getTimestamp()

            ###################

            previousSnapshot = graph

        return membershipChanges

    """
    Print out all recruitment changes in the list 
    @param changes: dictionary with node ID and timestamp 
    """
    def printDetectedChanges(self,changes):
        print("Recruitment events:")
        for nodeID, timestamp in changes.items():
            print("Resource ", nodeID," at ", timestamp.strftime("%d/%m/%Y, %H:%M:%S") )



    """
    Print to CSV
    @param changes : dictionary with node ID and timestamp
    @param writer: writer pointer to open file
    """
    def printToCSV(self, changes, writer):

        try:


        # write all the changes to the file
            for nodeID, timestamp in changes.items():
                writer.writerow([timestamp.strftime("%Y-%m-%d %H:%M:%S"),"Recruitment", "Resource "+ str(nodeID)])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')



    def printToCSVWithID(self, changes, writer):

        try:

            for nodeID, timestamp in changes.items():
                writer.writerow([timestamp.strftime("%Y-%m-%d %H:%M:%S"),"Recruitment",str(nodeID), "Resource "+ str(nodeID)])


        except Exception as e:
            print('File does not exist. Please provide the correct CSV file name to write the changes to.')