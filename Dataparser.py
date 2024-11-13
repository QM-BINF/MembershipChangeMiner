# parse the input data
import csv
import io
import argparse

import time
import re
from time import mktime
from datetime import datetime

import Object
import Resource
import CollaborationSession
import CollaborationEvent
import WorkSession
import WorkEvent

class DataParser:
    def __init__(self):
        self.resources = []
        self.objects = []
        self.collabSessions = []
        self.collabEvents = []
        self.workSessions = []
        self.workEvents = []


    def getResourceList(self):
        return self.resources

    def getObjectList(self):
        return self.objects

    def __getCollabSessionsList(self):
        return self.collabSessions

    def getCollabEventsList(self):
        return self.collabEvents

    def getWorkEventsList(self):
        return self.workEvents

    #@param resourcesFile: CSV file of all resources and their ID
    #@param objectsFile: CSV file of all objects with their ID
    #@param collabSessionsFile: CSV file of all collab sessions
    #@param workSessionsFile:  CSV file of all work sessions
    def parseAllData(self,resourcesFile,objectsFile, collabSessionsFile, workSessionsFile):
        self.__parseResources(resourcesFile)
        self.__parseObjects(objectsFile)
        self.__parseCollabSessions(collabSessionsFile)
        self.__createCollabEvents()
        self.__parseWorkSessions(workSessionsFile)
        self.__createWorkEvents()

    def __parseResources(self, resourcesFile):
        file = resourcesFile
        try:
            with io.open(file, encoding="utf-8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                headerParsed = False

                for row in csv_reader:
                    if not headerParsed:
                        headerParsed = True
                    else:
                        # make resource
                        self.makeResource(int(row[0]), row[1])


        except Exception as e:
            print('File does not exist. Please provide the correct resource CSV file name.')



    # Make a Resource object
    # @param id : numerical ID of resource
    # @param label: string label of resource
    def makeResource(self, id, label):
        resource = Resource.Resource(id, label)
        self.resources.append(resource)


    #Parser for a CSV file with objects: first ID, then object label
    def __parseObjects(self, objectsFile):
        file = objectsFile

        try:
            with io.open(file, encoding="utf-8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                headerParsed = False

                for row in csv_reader:
                    if not headerParsed:
                        headerParsed = True
                    else:
                        # make object
                        self.makeObject(int(row[0]), row[1])


        except Exception as e:
            print('File does not exist. Please provide the correct object CSV file name.')





    # Make a Object object
    # @param id : numerical ID of object
    # @param label: string label of object
    def makeObject(self, id, label):
        obj = Object.Object(id,label)
        self.objects.append(obj)

    #parser for CSV file containing collaboration sessions
    #@param collabSessionsFile:
    def __parseCollabSessions(self, collabSessionsFile):

        file = collabSessionsFile

        try:
            with io.open(file, encoding="utf-8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                headerParsed = False

                for row in csv_reader:
                    if not headerParsed:
                        headerParsed = True
                    else:
                        # make collabsession
                        self.makeCollabSession(int(row[0]), row[1], int(row[2]),row[3],int(row[4]),row[5],row[6],row[7],row[8])


        except Exception as e:
            print('File does not exist. Please provide the correct collaboration sessions CSV file name.')
            print(e)




    #Make a CollaborationSession object
    #@param resourceID1:  numerical ID of resource 1
    #@param resourceLabel1: string label of resource 1
    #@param resourceID2: numerical ID of resource 2
    #@param resourceLabel2: string label of resource 2
    #@param objectID: numerical ID of object
    #@param objectLabel: string label of object
    #@param firstTmstp: string containing the first timestamp of the session
    #@param lastTmstp: string containing the last timestamp of the session
    #@param medianTmstp: string containing the median timestamp of the session
    def makeCollabSession(self,resourceID1, resourceLabel1, resourceID2, resourceLabel2, objectID, objectLabel, firstTmstp, lastTmstp, medianTmstp):
        #find resources
        resource1 = self.findResourceByID(resourceID1)
        resource2 = self.findResourceByID(resourceID2)
        #find object
        obj = self.findObjectByID(objectID)

        #convert timestamps
        firstTimestamp = datetime.strptime(firstTmstp,"%d/%m/%Y %H:%M:%S")
        lastTimestamp =  datetime.strptime(lastTmstp,"%d/%m/%Y %H:%M:%S")
        medianTimestamp =  datetime.strptime(medianTmstp,"%d/%m/%Y %H:%M:%S")

        #make collab session object
        collabSession = CollaborationSession.CollaborationSession(resource1, resource2,obj,firstTimestamp, lastTimestamp, medianTimestamp)
        self.collabSessions.append(collabSession)

        #also add it to resources
        resource1.addCollabSession(collabSession)
        resource2.addCollabSession(collabSession)

    """
    Collaboration sessions are between 2 resources on a single object and have a duration.
    We want to convert this to an event that is instantaneous, as the duration is negligible
    There could be multiple collab sessions for a resource pair at the same timestamp (as it is represented per object) 
    We want to convert this to a single collab event at that timestamp (but on multiple objects then) 
    """
    def __createCollabEvents(self):
        #create for each collaboration session a collab event EXCEPT if the resource pair and timestamp is the same
        for cs in self.collabSessions:
            resource1 = cs.getSource()
            resource2 = cs.getTarget()
            #we set the timestamp of the collab event to the first timestamp
            #other options could be: last and median timestamp
            timestamp = cs.getFirstTimestamp()
            object = cs.getObject()
              #search if there is already a collab event with this session's details
            ce = self.searchCollabEvent(resource1,resource2,timestamp)
            #if there is no existing collab event between the resources at this timestamp, create a new one
            if not ce:
                #else make a CollaborationEvent object
                collabEvent = CollaborationEvent.CollaborationEvent(resource1, resource2,timestamp,object)
                self.collabEvents.append(collabEvent)
            else:
                #just add this object to the collab event
                ce.addObject(object)



    #parser for CSV file containing work sessions
    #@param workSessionsFile: CSV file containing the work sessions
    def __parseWorkSessions(self, workSessionsFile):

        file = workSessionsFile

        try:
            with io.open(file, encoding="utf-8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                headerParsed = False

                for row in csv_reader:
                    if not headerParsed:
                        headerParsed = True
                    else:
                        # make worksession
                        self.__makeWorkSession(int(row[0]), row[1], row[2],row[3],row[4])


        except Exception as e:
            print("No file with work sessions is provided. Resource recruitment will be done based on a resource's first collaboration event.")
            print(e)


    #Make a WorkSessions object
    #@param resourceID:  numerical ID of resource
    #@param resourceLabel: string label of resource
    #@param firstTmstp: string containing the of first timestamp of the session
    #@param lastTmstp: string containing the last timestamp of the session
    #@param medianTmstp: string containing the median timestamp of the session
    def __makeWorkSession(self,resourceID, resourceLabel,  firstTmstp, lastTmstp, medianTmstp):
        #find resource
        resource = self.findResourceByID(resourceID)


        #convert timestamps
        firstTimestamp = datetime.strptime(firstTmstp,"%d/%m/%Y, %H:%M:%S")
        lastTimestamp =  datetime.strptime(lastTmstp,"%d/%m/%Y, %H:%M:%S")
        medianTimestamp =  datetime.strptime(medianTmstp,"%d/%m/%Y, %H:%M:%S")

        #make work session object
        workSession = WorkSession.WorkSession(resource,firstTimestamp, lastTimestamp, medianTimestamp)
        self.workSessions.append(workSession)

        #also add it to resources
        resource.addWorkSession(workSession)


    """
    Work sessions  have a duration.
    We want to convert this to an event that is instantaneous, as the duration is negligible
    """
    def __createWorkEvents(self):

        for ws in self.workSessions:
            resource = ws.getResource()
            #we set the timestamp of the collab event to the first timestamp
            #other options could be: last and median timestamp
            timestamp = ws.getFirstTimestamp()

            workevent = WorkEvent.WorkEvent(resource,timestamp)
            self.workEvents.append(workevent)




    """
    @param resource1 : source resource 
    @param resource2: target resource 
    @param timestamp: timestamp of the collaboration  
    @return CollaborationEvent object that is between these 2 resources at that timestamp OR None if that doesn't exist
    """
    def searchCollabEvent(self,resource1,resource2, timestamp):
        ces = [x for x in self.collabEvents if (x.concernsResources(resource1,resource2) and x.getEventTimestamp() == timestamp)]
        if not ces:
            return None
        else :
            return ces[0]

    #@param ID of resource
    #@returns Resource object with that ID
    def findResourceByID(self, ID):
        for resource in self.resources:
            if ID == resource.getID():
                return resource

    #@param ID of object
    #@returns Object object with that ID
    def findObjectByID(self,ID):
        for object in self.objects:
            if ID == object.getID():
                return object



