#Class that focuses on parsing the data on resources, objects and event into temporal graphs
import Graph
import TemporalGraph
from datetime import datetime,timedelta
import sys
import CommunityDetection
import operator
import argparse
import csv
import io
class GraphEvolutionParser:

    """'
    @param resources:  list of Resource objects representing all resources in the graph
    @param objects:  list of Object objects representing all objects in the graph
    @param collabEvents:  list of CollaborationEvents objects representing all collaboration events between resources
    These will be sorted here
    @param workEvents: list of WorkEvent objects representing all work events of all resources
    @param tieStrengthHandler: TieStrengthHandler object that holds all mechanisms of tie strength evolution

    '"""
    def __init__(self, resources, objects, collabEvents,workEvents, tieStrengthHandler):
        self.resources = resources
        self.objects = objects
        #sort collab events
        collabEvents = self.sortCollabEvents(collabEvents)
        self.collabEvents = collabEvents
        workEvents = self.sortWorkEvents(workEvents)
        self.workEvents = workEvents
        #Filter out for each resource the timestamp at which they first appear (either work event or collaboration event)
        self.resourcePopUpTime = self.constructFirstResourceTimestampList()
        self.tieStrengthHandler = tieStrengthHandler

        #dict of when each edge will disappear
        self.edgeRemovalTimes = {}


        #For each edge keep the timestamp of the last event on the edge and its weight at that point
        self.lastEventOnEdge = {}





    #sort the collaboration events based on their event timestamp
    def sortCollabEvents(self,collabEvents):
    #sort them based on the event timestamp
        collabEvents.sort(key= lambda x: x.getEventTimestamp())

        return collabEvents

    def sortWorkEvents(self,events):
    #sort them based on the event timestamp
        events.sort(key= lambda x: x.getEventTimestamp())

        return events

    """
    Make a dict for each Resource the first timestamp they appear (timestamp of work event or collaboration event) 
    @return dict with Resource object as key and timestamp (date time object) as value
    """
    def constructFirstResourceTimestampList(self):
        firstWorkEvents = {}
        firstCollabEvents = {}
        firstTimestamps = {}
        #search for each resource their first work event and their first collaboration event : add the earliest timestamp
        #first work event : the events are already ordered
        for we in self.workEvents:
            resource = we.getResource()
            if not resource in firstWorkEvents:
                #add this event as it's the first we encounter
                firstWorkEvents[resource] = we.getEventTimestamp()

        #first collaboration event : the events are already ordered
        for ce in self.collabEvents:
            resource1, resource2 = ce.getTupleFormat()
            if not resource1 in firstCollabEvents:
                firstCollabEvents[resource1]= ce.getEventTimestamp()
            if not resource2 in firstCollabEvents:
                firstCollabEvents[resource2]= ce.getEventTimestamp()

        #These two lines should not be necessary since all resources should at least have one work event!
        allResources = list(firstWorkEvents.keys())
        allResources.extend(r for r in  list(firstCollabEvents.keys()) if r not in allResources)

        for resource in allResources:
            ts1 = firstWorkEvents.get(resource)
            ts2 = firstCollabEvents.get(resource)  #returns None if it doesnt exist in the dict
            if ts1 and ts2:
                if ts1 < ts2:
                    firstTimestamps[resource] = ts1
                else:
                    firstTimestamps[resource] = ts2
            #one or both are None
            elif ts1:
                firstTimestamps[resource]  = ts1
            #This is probably also not relevant as all resources have at least a work event, so it will always be the collaboration event timestamp that is None
            elif ts2:
                firstTimestamps[resource] = ts2

            #else the resource doesn't have a work or collab event   --> should not happen!
            else:
                sys.exit("The resource ", resource.getID(), " ", resource.getLabel(), " does not have a work or collaboration session and therefore shouldn't exist!")


        return firstTimestamps



    """
    Create a TemporalGraph object representing the graphs for each time slice within the boundaries
    Each event will be a separate graph and if there is more than the time slice in between events, 
    intermediate Graphs are added that display the network every x minutes (indicated by the time slicing argument)
    @param begin_timestamp 
    @param end_timestamp 
    @param time_slice_unit: unit of measurement for the time slicing in minutes
            This does not have to be a multiple of the timestep variable
            This does not even have to be larger than the timestep variable in TieStrengthHandler, but most logically it will be larger as the timestep is one step in the decay function while the timeslice is a larger window over time where you want to see the evolution of the tie strength up until that point 
    @returns TemporalGraph object representing the temporal graph 
    """
    def createTemporalGraph(self,begin_timestamp, end_timestamp,time_slice_unit):
        # (end_timestamp - begin_timestamp ) / time_slice_unit = how many graphs need to be added to the temporal graph
        #This is the length of the temporal graph
        numberOfGraphs = 0
        listOfGraphs = []

        #make the first empty graph
        g = Graph.Graph()
        #set the current time as the current graph timestamp
        g.setCurrentWeightsTimestamp(begin_timestamp)

        #calculate graph snapshots
        currentTime = begin_timestamp
        endReached = False
        while not endReached:
            #make a new snapshot , returns the snapshot Graph object and the new point in time we're currently at
            snapshot,currentTime = self.makeNewSnapshot(currentTime,time_slice_unit,end_timestamp,g)
            if snapshot:

                #add to list of graph object
                listOfGraphs.append(snapshot)
                numberOfGraphs += 1
                #set new snapshot as the current last graph
                g = snapshot

            #if we reached the end timestamp, stop creating snapshots
            if currentTime == end_timestamp :
                endReached = True

        #create the temporal graph object
        temporalGraph = TemporalGraph.TemporalGraph(numberOfGraphs,listOfGraphs)

        return temporalGraph



    """
    @param currentTime 
    @param timeSliceUnit:  the time slice in minutes 
    @param endTimestamp:  timestamp of the last graph 
    @param graph : Graph object representing the graph at the currentTime 
    @returns Graph object of the graph of either the time the next event takes place (collaboration or work) or currentTime+timeSliceUnit from now if there is no event in that timespan 
             updated time: either the timestamp of the next event or currentTime+timeSliceUnit from now if there is no event in that timespan
    """
    def makeNewSnapshot(self,currentTime,timeSliceUnit,endTimestamp,graph):
        #search next event timestamp
        #if this timestamp falls before currentTime + timeSliceUnit then a graph is created for this event's timestamp
        #next event within timeframe ]currentTime, currentTime + timeSliceUnit]
        #could be a collaboration event OR a work event (a new node appears)
        nextSliceTimestamp = currentTime + timedelta(minutes = timeSliceUnit)
        #if this is beyond the endTimestamp, set it to the endTimestamp
        if nextSliceTimestamp > endTimestamp:
            nextSliceTimestamp = endTimestamp

        #search collaboration events
        nextTimestamp = self.searchNextInteractionTimestampWithinTimeFrame(currentTime,nextSliceTimestamp)
        #could also be an event concerning a node (example: node appearing)
        nextNodeEventTimestamp = self.searchNextNodeEventWithinTimeFrame(currentTime,nextSliceTimestamp)
        #could also be an event on the disappearance of an edge
        nextEdgeRemovalTimestamp = self.searchNextEdgeRemovalTimestampWithinTimeFrame(currentTime,nextSliceTimestamp)

        #select the relevant next timestamp from the 3 options
        nextTimestamp = self.selectFirstEventTimestampOutOfThree(nextTimestamp,nextNodeEventTimestamp,nextEdgeRemovalTimestamp)

        #there is an event in the next
        if nextTimestamp is None:
            #there is no event , calculate for currentTime + timeslice == nextSliceTimestamp
            #NOTE: if you only want graph snapshots for events, not for time slices: leave this as a comment
            #NOTE:  if you want to work with time increments then uncomment this and comment #snapshot = None
            nextTimestamp = nextSliceTimestamp
            #snapshot = self.calculateSnapshotForTS(graph,nextSliceTimestamp)
            snapshot = None

        else:
            #calculate for the next event on nextTimestamp
            snapshot = self.calculateSnapshotForTS(graph,nextTimestamp)

        return snapshot,nextTimestamp

    """
        Search the dictionary with edge removal times to find whether one takes place between ] beginTS, endTS]
        @param beginTS datetime object of first timestamp of window
        @param endTS datetime object of last timestamp of window 
        @returns the timestamp of the first event within the window
    """
    def searchNextEdgeRemovalTimestampWithinTimeFrame(self,beginTS, endTS):
        # firstTS between ]beginTS, endTS]
        #dict is unordered, make it into an ordered list
        orderedTimes = []
        for edge, time in self.edgeRemovalTimes.items():
            if beginTS < time and time <= endTS:
                orderedTimes.append(time)
        #if there is at least one candidate in the window
        if orderedTimes:
            orderedTimes.sort()
            return orderedTimes[0]

        return None





    """
    Search the collaboration events list to find whether a collaboration events takes place between ] beginTS, endTS]
    @param beginTS datetime object of first timestamp of window
    @param endTS datetime object of last timestamp of window 
    @returns the timestamp of the first event within the window
    """
    def searchNextInteractionTimestampWithinTimeFrame(self,beginTS, endTS):

        #firstTS between ]beginTS, endTS]
        nextTS = None
        #collabEvents are ordered
        for ce in self.collabEvents:
            ts = ce.getEventTimestamp()
            if ts > endTS:
                return nextTS
            elif beginTS < ts:
                return ts

        return nextTS

    """
    Search the resourcePopUpTime list to find whether a relevant node pop up event takes place between ] beginTS, endTS]
    @param beginTS datetime object of first timestamp of window
    @param endTS datetime object of last timestamp of window 
    @returns the first timestamp  within the window and None if there is none 
    """
    def searchNextNodeEventWithinTimeFrame(self, beginTS, endTS):
        #firstTS between ]beginTS, endTS]
        #resourcePopUp is an unordered dict, so make it a list and order it
        orderedTimes = []
        #the event represents node popup
        for key, time in self.resourcePopUpTime.items():
            if beginTS < time and time <= endTS:
                orderedTimes.append(time)
        # if there is at least one candidate in the window
        if orderedTimes:
            orderedTimes.sort()
            return orderedTimes[0]

        return None



    """
        @param firstTS: datetime object or None
        @param secondTS: datetime object or None
        @param thirdTS: datetime object or None
        @return first timestamp or none
    """
    def selectFirstEventTimestampOutOfThree(self,firstTS,secondTS, thirdTS):
        # if all three are timestamps
        if firstTS and secondTS and thirdTS:
            resultingTS = min(firstTS,secondTS,thirdTS)
        #if one of the three is at least none, we can pass this on to the function with 2
        else:
            if not firstTS:
                resultingTS = self.selectFirstEventTimestamp(secondTS,thirdTS)
            elif not secondTS:
                resultingTS = self.selectFirstEventTimestamp(firstTS,thirdTS)
            else:
                resultingTS = self.selectFirstEventTimestamp(firstTS,secondTS)

        return resultingTS

    """
    @param firstTS: datetime object or None
    @param secondTS: datetime object or None
    @return first timestamp or none
    """
    def selectFirstEventTimestamp(self,firstTS,secondTS):
        #if they are both datetime object, return the earliest time
        #if they are exactly the same it doesn't matter which one we return
        if firstTS and secondTS:
            if firstTS < secondTS:
                return firstTS
            else:
                return secondTS
        #Else one of the two is None
        elif firstTS:
            return firstTS
        elif secondTS:
            return secondTS
        #or both are None
        else:
            return None





    """
    Update the graph to represent the graph at the next timestamp:
    Update the existing tie strengths (decay + if an event happens increase the strength) 
    Look for new ties 
    @param graph: current graph as a  Graph object 
    @param timestamp:  timestamp for the new representation of the graph 
    @returns graph object representing the new graph at timestamp 
    """
    def calculateSnapshotForTS(self,graph,timestamp):
        #handle existing edges: update based on decay function up until this point
        newGraph = graph.deepCopy()
        #in this newGraph we can alter the edge weights
        #No events take place between the current graph and the next timestamp : if there is an event the first one happens at timestamp !
        #so no event handling of edges is necessary here
        removedEdges = newGraph.decayEdges(self.tieStrengthHandler,timestamp,self.lastEventOnEdge)

        #find all node events that take place on the timestamp
        #First we have the appearance of new resources (their first work event or collab event (whichever is first) takes place at timestamp)
        popupResources = self.findNodeEventsAtTimestamp(timestamp)
        newGraph.handleNodeEvents(popupResources)

        #update strength if interaction takes place
        #find all interactions that take place on the timestamp : returns array of collaboration events
        interactions = self.findInteractionsAtTimestamp(timestamp)
        #update also when the last event on an edge took place and its weight
        newGraph.handleInteractions(interactions,self.tieStrengthHandler, self.lastEventOnEdge,timestamp)



        #Now all edge weights are updated, update the timestamp for the edge weights
        newGraph.setCurrentWeightsTimestamp(timestamp)

        # update edge removal timestamps which are the times we need to take additional snapshots
        self.updateRemovalSnapshotTimes(removedEdges, interactions, newGraph)

        return newGraph


    """
    @ TS: timestamp 
    @ returns list of CollaborationEvent objects that have TS as their event timestamp
    """
    def findInteractionsAtTimestamp(self,TS):
        #There can be multiple collab events at the same timestamp but between different resources
        #For each resource pair there can be only one event at a certain timestamp
        collabEventsAtTS = [x for x in self.collabEvents if x.getEventTimestamp() == TS]
        return collabEventsAtTS

    """
    @TS: timestamp as a datetime object 
    @return list of Resources that experience a pop up event: they are new to the graph and should be added 
    """
    def findNodeEventsAtTimestamp(self,TS):
        popupResources = [r for r,timestamp in self.resourcePopUpTime.items() if timestamp == TS]
        return popupResources


    """
    Enhance the temporal graph with information about the teams of nodes 
    Each graph object in the snapshot list will be analyzed and info will be added about the team 
    Added to each graph object: a networkx graph representing the graph, the communities 
    @param temporalGraph: a temporalgraph object with graph snapshots 
    @return return nothing but alters the temporalGraph object directly 
    """
    def detectTemporalTeams(self,temporalGraph):
        graphSnapshots = temporalGraph.getListOfGraphs()
        previousCommunities = None
        for snapshot in graphSnapshots:
            netwxGraph = snapshot.createNetworkxGraph()
            ### community detection: pass the communities of the previous snapshot; if no previous snapshot pass None
            # new nodes do not belong to a community yet and need to be added as a separate community
            previousCommunities = CommunityDetection.processPreviousCommunityState(netwxGraph.nodes(), previousCommunities)
            communities = CommunityDetection.communityDetection(netwxGraph, previousCommunities)
            previousCommunities = communities.copy()

            snapshot.setTeams(communities)


    """
    Update the list of snapshots on edge removal: 
    remove edges that got removed in this snapshot ;  update the removal time for edges on which an interaction took place 
    @param removedEdges  list of Edge objects that need to be removed from the snapshot times list 
    @param interactions list of CollaborationEvent objects : for each edge there can only be a single event or none
    @param graph object 
    """
    def updateRemovalSnapshotTimes(self, removedEdges, interactions, graph):



        #remove edges that do not exist anymore
        for edge in removedEdges:
            del self.edgeRemovalTimes[edge]

        currentTS = graph.getCurrentWeightsTimestamp()
        #update the times for the edges on which an interaction happens
        #for each edge there can only be a single collaboration event in this list
        #an event happens at this point, so this is the starting point for the decay function so there is no need to look up the timestamp of the last event
        for collabEvent in interactions:
            resourcesTuple = collabEvent.getTupleFormat()
            #search Edge between these 2 resources
            edge = graph.findEdge(resourcesTuple[0], resourcesTuple[1])
            #Edge SHOULD exist
            if not edge:
                sys.exit("Edge between ", resourcesTuple, "  should exist already but does not.")

            newTS = self.tieStrengthHandler.getPredictedTSofDecay(graph.findEdgeWeight(edge),currentTS)

            #update this in the dict
            self.edgeRemovalTimes[edge] = newTS







