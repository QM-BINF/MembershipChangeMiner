# **Membership Change Miner**
The code in this repository encompasses an implementation of an approach to extract membership changes from event data on work and collaboration sessions.
To this end, the work and collaboration behavior of resources is modeled as continuous network evolution using a temporal graph consisting of individual graph snapshots. The approach discovers membership changes throughout this network evolution.
The development of this project is part of the PhD. disseration of L. Jooken, supported by the BOF funding of Hasselt University. 

Team membership changes describe the manner in which members flow through the different teams in an organizational network, resulting in changing team compositions. These changes indicate time points in the lifecycle of the network at which the network structure atomically changes, which can guide targeted analyses. 


The following membership changes can currently be discovered: 
- ***Recruitment***: a single member enters the organizational pool
- ***Expansion***:  a single member enters a team  
- ***Expulsion***: a single member leaves a team 
- ***Reassignment***: a single member leaves its team and enters a different team
- ***Group merge***: two distinct teams come together to form a single team
- ***Group partition***: a subgroup splits off from the origin team to become a separate team 
- ***Group dissolution***: all members of a single team leave the team causing the team to cease to exist




## **Input data files**
The membership changes can be discovered from data on work and collaboration sessions. 

A ***work session*** represents a time window in which a member worked.

A ***collaboration session*** represents a time window in which two members collaborated on a specific object. 

This data can be produced by the RFM Collaboration Miner project from event data specifying the timestamp at which a member worked on a specific object.

The required input files must adhere to the following format, all must include headers.

### **Resources**

List of all resources (i.e., members) of the organizational network. 

| ResourceID | Label |
|-------------|---------------|
| numerical | text |

### **Objects**

List of all objects that resources work and collaborate on with the preferred granularity. For example: files, chapters, projects, ...

| ObjectID  | Label |
|-----------|----------------|
| numerical | text |

### **Work sessions** 

List of all time windows in which a member worked.

| ResourceID | ResourceLabel | FirstTimestamp | LastTimestamp | MedianTimestamp |
|-------------|---------------| --------- | ----------- | ----------- |
| numerical   | text          | d/m/YYYY H:M:S | d/m/YYYY H:M:S | d/m/YYYY H:M:S |

With
- FirstTimestamp being the timestamp of the first event in the window
- LastTimestamp being the timestamp of the last event in the window 
- MedianTimestamp being the timestamp of the median event in the window

All resources must appear in the resource file.

### **Collaboration sessions**

List of all time windows in which two members collaborated on a specific object. 

| ResourceID1 | ResourceLabel1 | ResourceID2 | ResourceLabel2 | Object    | ObjectName | FirstTimestamp | LastTimestamp | MedianTimestamp |
|-------------|----------------|-------------|----------------|-----------|------------| ----------- | ----------- | ----------- |
| numerical   | text           | numerical   | text           | numerical | text       | d/m/YYYY H:M:S | d/m/YYYY H:M:S | d/m/YYYY H:M:S |

With
- FirstTimestamp being the timestamp of the first event in the window
- LastTimestamp being the timestamp of the last event in the window 
- MedianTimestamp being the timestamp of the median event in the window

All resources must appear in the resource file; all objects must appear in the object file.



## **Usage** 
In order to run the program, call upon *"main.py"* and add the following data as arguments. 

- **-r**  pass the file name of the resources CSV file
- **-o**  pass the file name of the objects CSV file 
- **-cs**  pass the file name of the collaboration sessions CSV file 
- **-ws**  pass the file name of the work sessions CSV file
- **-pod**  pass the period of decay in minutes. I.e., after how long without collaboration does the collaboration relationship between two resources disappear? 
- **-bts**  pass the begin timestamp of the project (the period you want to analyze) in the format d/m/YYYY H:M:S. (Note that it will consider this to be the start of the project and therefore start with an empty graph. An intermediate snapshot to start from is not yet supported.)
- **-ets** pass the end timestamp of the project in the format d/m/YYYY H:M:S

By illustration:
```python
main.py -r resources.csv -o objects.csv -cs collabsessions.csv -ws worksessions.csv -pod 24480 -bts "01/01/2024" -ets "01/12/2024"
```

## **Customization options**
Some flexibility is built into the code. Included here is a list of the most common options that can be changed. 


### **Timestamp representing the events**

Work and collaboration sessions are transformed into instantaneous work and collaboration events. By default, the first timestamp of the session is selected to represent the time of the corresponding event.
This option can be changed so that either the median timestamp or the last timestamp respresents the time of the event. 
This can be changed in *"DataParser.py"* by changing the code to the desired function.


```python 
    def __createWorkEvents(self):
    
        for ws in self.workSessions:
            resource = ws.getResource()
            #we set the timestamp of the collab event to the first timestamp
            #other options could be: last and median timestamp
            timestamp = ws.getFirstTimestamp()
            timestamp = ws.getMedianTimestamp() 
            timestamp = ws.getLastTimestamp()
    
            ...
            
    def __createCollabEvents(self):
        
         for cs in self.collabSessions:
            resource1 = cs.getSource()
            resource2 = cs.getTarget()
            #we set the timestamp of the collab event to the first timestamp
            #other options could be: last and median timestamp
            timestamp = cs.getFirstTimestamp()
            timestamp = cs.getMedianTimestamp() 
            timestamp = cs.getLastTimestamp()
            
            ...

```

### **Community detection algorithm**

The detection of teams in the temporal graph is based on a community detection algorithm. 
You have the option to switch between three different supported community detection algorithms: 

- Clauset-Newman-Moore greedy modularity maximization
- Louvain community detection
- Leiden community detection  *(default)*

The algorithm can be set in *"CommunityDetection.py"* by uncommenting the desired algorithm and commenting the other two. 

```python
    def communityDetection(graph, previousPartition):
        #Uncomment the community detection algorithm of your choice: Louvain, Clauset Newman Moore, or Leiden
    
        #Different community detection options
        #Louvain
        #partition = louvainCommunityDetection(graph, previousPartition)
    
        #Clauset newman moore
        #partition = CNMcommunityDetection(graph)
    
        #Leiden
        partition = leidenCommunityDetection(graph,previousPartition)
    
        return partition

```
### **Recruitments of the first snapshot**
As one might start analyzing the project not from the beginning, but from an intermediate point into the project timeline, the first snapshot of the temporal graph does not contain any changes. 
Therefore, no recruitment changes are included for the members that appear in this first snapshot.

To include recruitment changes for the resources appearing in this first snapshot, change the code in *"RecruitmentChange.py"* to the following. 

```python

    def detectChanges(self,temporalGraph, expansionChangeMiner, expulsionChangeMiner):
        ...

            #########else:  first snapshot: all nodes are considered to be 'new'
            #but since we don't often start at the beginning but somewhere in the middle of the dataset,
            #we do not consider this first snapshot to contain any changes
            #if you do wish to add these nodes as recruitments, uncomment the following lines

            else:
                currentNodes = graph.getListOfNodeIDs()
                for node in currentNodes:
                    membershipChanges[node] = graph.getTimestamp()

            ###################

            ...

```




### **Reassignments over multiple snapshots**

A reassignment change can take place over multiple snapshots. The time window in which this reassignment must take place is set to 3 days by default. 
This can be changed in *"ReassignmentChange.py"*.

```python 
  def findReassignmentChangesOverMultipleSnapshots(self,temporalGraph,graphSnapshots, expansionChangeMiner, expulsionChangeMiner):
        timewindow = timedelta(days = 3)
        ...
```


## **Output**
### **Print the detected changes**
The output of the approach is a list of membership changes. This list can be printed in the console, or printed to CSV. 
To print the output, uncomment the desired line in *"main.py"*.
There are two options to print to CSV: 

- *printDetectedChangesToCSV* : prints out the list of all detected changes 
- *printDetectedChangesToCSVWithResourceID* : prints out the list of detected changes for each resource ID separately. This causes changes that include multiple resources to be repeated multiple times in the output, once for every resource involved. This makes sorting and analyzing changes per resource easier.

```python 
        #Uncomment the next line to print in the console
        membershipChangeMonitor.printDetectedMembershipChanges()
        #Uncomment the next line to print to CSV
        membershipChangeMonitor.printDetectedChangesToCSV("DetectedChanges.csv")
        membershipChangeMonitor.printDetectedChangesToCSVWithResourceID("DetectedChangesByID.csv")
```


### **Print the collaboration events**
The code contains an additional function to print the collaboration events to a CSV file, which can be found in *"Output.py"*. In order to use this, the collaboration events must be requested from the DataParser object using the function *"getCollabEventsList()*". 



## **Network visualization**

There is an option to visualize the created snapshots of the temporal graph to obtain a view on the continuous network evolution. 
This functionality can be turned on by uncommenting the following code in *"main.py"*.

```python
   #visualize the temporalgraph
    graphViz = GraphVisualizer.GraphVisualizer()
    graphViz.visualizeTemporalGraph(temporalGraph)
```

Currently, a snapshot is made for each collaboration event, each node pop up, and each point at which a relationship disappears (i.e., the key moments). If you want there to be additional intermediate snapshots for long periods in which no such key moment takes place, you can set the time slice argument. 
In the absence of these key moments it shows snapshots for every time slice. 

The default time slice is set to 3 days, meaning if no key moment happens, a snapshot is added for every 3 days.

Currently, the time slice argument is disabled. To turn it on, uncomment the following code in *"GraphEvolutionParser.py"*. The resulting code should look like this.

```python
    if nextTimestamp is None:
        #there is no event , calculate for currentTime + timeslice == nextSliceTimestamp
        #NOTE: if you only want graph snapshots for events, not for time slices: leave this as a comment
        #NOTE:  if you want to work with time increments then uncomment this and comment #snapshot = None
        nextTimestamp = nextSliceTimestamp
        snapshot = self.calculateSnapshotForTS(graph,nextSliceTimestamp)
        #snapshot = None
```


  
## **Demo**
The project contains a demo on artificial data. The case concerns an organization consisting of three teams, each consisting of three to five members, a product owner, a scrum master, and a solution architect.
The collaboration consists of daily scrum meetings, biweekly sprint demos, and bi-weekly sprint plannings. 
The attendance at the different meetings can differ between roles. 

|                        | Team 1 | Team 2 | Team 3 | 
|------------------------|---- |---- |---- |
| **Product owner**      | Jef Mendel | Viv Aldi | Jef Mendel | 
| **Scrum master**       | Angelo Michel | Angelo Michel | Angelo Michel | 
| **Solution architect** | Caroll Lewis | Caroll Lewis | Caroll Lewis | 
| **Initial team**       | Christie Agath, Martin Stevenson, Hugo Victor, Adam Douglas, Dave Alanies | Michelle Davids, Dennis Hugh, An Millic | Tom Washing, An Iston, Berry Halle |

|                               | Attendance                                                                                                                                    | 
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------| 
| **Daily scrum meeting**       | All team members, the team’s product owner, scrum master, and solution architect (the latter only 10% attendance rate)                        | 
| **Bi-weekly sprint demo**     | The team members (each has 50 % attendance rate), the team’s scrum master, the team’s solution architect, and the product owners of all teams |
| **Bi-weekly sprint planning** | All team members, the team’s scrum master and product owner                                                                                   |

The required data can be found in the following files: 
- AI_resources.csv
- AI_objects.csv 
- AI_collab_sessions.csv 
- No work sessions are provided. The resource recruitment is done based on a resource's first collaboration event.
- Period of decay is set to 17 days


As the required data is set by default, the demo can be run without arguments: 
```python
main.py 
```
This results in a list of 446 membership changes. 

## **Contact**
If you have any questions, please contact the Business Informatics research team at Hasselt University.