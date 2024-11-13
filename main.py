import operator
import argparse
import csv
import Dataparser
import GraphEvolutionParser
from datetime import datetime
import TieStrengthHandler
import GraphVisualizer
import MembershipChangeMonitor
import Output


def main(resourcesFile,objectsFile,collabSessionsFile,workSessionsFile, periodOfTotalDecay,beginTS,endTS):
        #parse all data
        dataparser = Dataparser.DataParser()

        dataparser.parseAllData(resourcesFile,objectsFile,collabSessionsFile,workSessionsFile)


        resources = dataparser.getResourceList()
        objects = dataparser.getObjectList()
        collabEvents = dataparser.getCollabEventsList()
        workEvents = dataparser.getWorkEventsList()



        #Class that holds all mechanisms for tie decay and evolution
        #DEFAULT PARAMETERS
        timestep = 60*12
        jumpsize = 0.3
        scale = 30
        #the threshold and decay params can be set in this function if needed
        tieStrengthHandler = TieStrengthHandler.TieStrengthHandler(timestep,jumpsize,periodOfTotalDecay)

        graphEvolutionParser = GraphEvolutionParser.GraphEvolutionParser(resources,objects,collabEvents,workEvents,tieStrengthHandler)


        #The time slice argument is used to produce a visualization of the graph that shows all events as snapshots and in the absence of events it shows snapshots for every timeslice
        #currently the time slice mechanism is disabled in the createTemporalGraph function of the GraphEvolutionParser. If you want to turn it on, uncomment the necessary code in the GraphEvolutionParser file
        #time slice is now 3 days : this is to update the visualization: if no event happens, show every 3 days
        temporalGraph = graphEvolutionParser.createTemporalGraph(beginTS,endTS,4320)
        graphEvolutionParser.detectTemporalTeams(temporalGraph)


        #visualize the temporalgraph
        #graphViz = GraphVisualizer.GraphVisualizer()
        #graphViz.visualizeTemporalGraph(temporalGraph)

        #Identify membership changes
        membershipChangeMonitor = MembershipChangeMonitor.MembershipChangeMonitor(temporalGraph)
        membershipChangeMonitor.detectMembershipChanges()

        #Uncomment the next line to print in the console
        #membershipChangeMonitor.printDetectedMembershipChanges()
        #Uncomment the next line to print to CSV
        #membershipChangeMonitor.printDetectedChangesToCSV("DetectedChanges.csv")
        #membershipChangeMonitor.printDetectedChangesToCSVWithResourceID("DetectedChangesByID.csv")



########################################
#Test on artificial data
resourcesFile = "AI_resources.csv"
objectsFile = "AI_objects.csv"
collabSessionsFile = "AI_collab_sessions.csv"
workSessionsFile = None
periodOfTotalDecay = 17*24*60  #after 17 days total decay
beginTS = datetime.strptime("1/03/2022, 09:00:00", "%d/%m/%Y, %H:%M:%S")
endTS = datetime.strptime("1/03/2023, 01:00:00", "%d/%m/%Y, %H:%M:%S")

#parse the command line arguments
print("Parsing the arguments")
parser = argparse.ArgumentParser()
parser.add_argument("-r","--resources_filename",help="pass the resources CSV filename")
parser.add_argument("-o","--objects_filename",help="pass the objects CSV filename")
parser.add_argument("-cs","--collab_sessions",help="pass the collaboration sessions CSV filename")
parser.add_argument("-ws","--work_sessions",help="pass the work sessions CSV filename")
parser.add_argument("-pod","--period_of_decay",help = "After how long no collaboration does the collaboration relationship between two resources disappear? (in minutes) ")
parser.add_argument("-bts","--beginTS",help = "pass the begin timestamp of the project (period you want to analyze) in the format %d/%m/%Y %H:%M:%S")
parser.add_argument("-ets","--endTS",help = "pass the end timestamp of the period you want to analyze in the format %d/%m/%Y %H:%M:%S")

args = parser.parse_args()
#If there is no resource file, assume that the test data is run
if args.resources_filename:
        resourcesFile = args.resources_filename
        objectsFile = args.objects_filename
        collabSessionsFile = args.collab_sessions
        workSessionsFile = args.work_sessions
        periodOfTotalDecay = int(args.period_of_decay)
        beginTS =  datetime.strptime(args.beginTS, "%d/%m/%Y %H:%M:%S")
        endTS =  datetime.strptime(args.endTS, "%d/%m/%Y %H:%M:%S")



#run the program
main(resourcesFile,objectsFile,collabSessionsFile,workSessionsFile,periodOfTotalDecay,beginTS,endTS)
