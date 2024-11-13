import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.cm as cm
import numpy as np
#alternative
from math import log10 , floor

import CommunityDetection

#Visualize a graph or temporal graph
class GraphVisualizer:

    def __init__(self):
        #list of graph and timestamp tuples
        self.graphSnapshotList = []
        self.positions = None       #positions of the nodes in the graph in the plotted window
        self.ax = None
        self.fig = None
        self.temporalGraphMaxWeight = None
        self.currentView = None
        self.slider = None

    """
    Visualizes the graph snapshots using a slider 
    @param temporalGraph: TemporalGraph object consisting of graph snapshots to visualize 
    """
    def visualizeTemporalGraph(self, temporalGraph):
        #get the max weight from the entire temporal graph
        self.temporalGraphMaxWeight = temporalGraph.getMaxWeight()
        #what if it's 0 meaning, there are no edges in none of the snapshots

        #we need to convert it to networkx graph objects
        graphSnapshots = temporalGraph.getListOfGraphs()
        self.createGraphSnapshotList(graphSnapshots)




        #create a plot window to plot the graphs
        self.createVizWindow(temporalGraph.getNumberOfGraphs())


    """
    For each graph in the list, create a networkx graph object and store this new list in the self.graphSnapshotList (overwrite)
    @param listOfGraphs : list of tuples (Graph objects sorted from earliest timestamp to latest , their timestamp)
    """
    def createGraphSnapshotList(self,listOfGraphs):
        graphxList = []
        for g in listOfGraphs:
            netwxGraph = g.getNetworkxGraph()
            communities = g.getTeams()

            ######
            nodeLabels={node: node for node in netwxGraph.nodes()}
            currentWeightsTimestamp = g.getCurrentWeightsTimestamp()
            weightLabelsInfo = nx.get_edge_attributes(netwxGraph,'weight')
            weights = weightLabelsInfo.values()
            #if there are no edges, there are no weights. Only if there are weights these need to be scaled and appropriate labels must be provided
            if weights:
                #round the weight labels for the visualization
                weightLabelsInfo = self.weightLabelRounding(weightLabelsInfo)
                #scale these for the plot
                scaledWeights = self.scaleWeightValues(weights)
            #if there are no edges
            else:
                #keep weightLabelsInfo as it is
                #do not scale the weights
                scaledWeights = weights

            #Tuple: (networkx graph, timestamp, scaled weights, labels for scaled weights, labels for nodes, community detection partitions
            graphxList.append((netwxGraph,currentWeightsTimestamp,scaledWeights,weightLabelsInfo,nodeLabels,communities))

        self.graphSnapshotList = graphxList




    """
    Fetch the correct graph snapshot to visualize based on the timeline slider 
    @returns tuple (networkx graph object, timestamp as a datetime object)
    """
    def remake_graph(self, r):
        return self.graphSnapshotList[r]



    """
    update the visualization using the slider 
    """
    def update(self, sliderNumber):
        graph_option = sliderNumber
        self.currentView = graph_option
        graph_to_show,timestamp, scaledWeights, weightLabels, nodeLabels, communities = self.remake_graph(graph_option)

        self.ax.clear()
        #remove frame around graph
        self.ax.axis("off")

        # community detection
        cmap = cm.get_cmap('viridis',max(communities.values())+1)
        ####
        #update the timestamp title
        plt.title(timestamp.strftime("%d/%m/%Y, %H:%M:%S"))
        # community detection
        nx.draw_networkx_nodes(graph_to_show,self.positions,communities.keys(),ax = self.ax,cmap=cmap,node_color=list(communities.values()),label = nodeLabels)
        nx.draw_networkx_labels(graph_to_show,self.positions,ax=self.ax,labels=nodeLabels,font_size=12)
        nx.draw_networkx_edges(graph_to_show,self.positions,ax = self.ax,width = scaledWeights)
        ####
        nx.draw_networkx_edge_labels(graph_to_show, self.positions, ax = self.ax,edge_labels = weightLabels, font_color = "red" )

        self.fig.canvas.draw_idle()

    """
    Button on forward click
    """
    def forward(self,vl):
        #check if we can go up
        if  self.currentView + 1  < len(self.graphSnapshotList):
            self.slider.set_val(self.currentView +1)




    """
    Button on backwards click
    """
    def backward(self,vl):
       #check if we can go down
        if  self.currentView -1  >= 0:
            self.slider.set_val(self.currentView -1)


    """
    Create a plot window with a slider to plot the temporal graphs 
    plots the first temporal graph 
    @param numGraphs : the number of  graph snapshots in this temporal graph 
    """
    def createVizWindow(self,numGraphs):
        self.fig, self.ax = plt.subplots()

        #remove frame around graph
        self.ax.axis("off")

        #take layout of the last graph, as this one contains all of the nodes TODO FOR FUTURE VERSION: when nodes start to disappear this does not hold true anymore
        self.positions = nx.spring_layout(self.graphSnapshotList[-1][0])


        #draw first graph
        graph_to_show,timestamp, scaledWeights, weightLabels, nodeLabels,communities = self.graphSnapshotList[0]
        self.currentView = 0


        # community detection
        cmap = cm.get_cmap('viridis',max(communities.values())+1)
        nx.draw_networkx_nodes(graph_to_show,self.positions,communities.keys(),ax = self.ax,cmap=cmap,node_color=list(communities.values()),label = nodeLabels)
        nx.draw_networkx_labels(graph_to_show, self.positions, ax=self.ax, labels=nodeLabels, font_size=12)
        nx.draw_networkx_edges(graph_to_show,self.positions,ax = self.ax,width = scaledWeights)
        ####

        nx.draw_networkx_edge_labels(graph_to_show, self.positions, ax = self.ax,edge_labels = weightLabels, font_color = "red" )

        plt.subplots_adjust(bottom=0.25)

        # Make a horizontal slider to control which graph is shown.
        axcolor = 'lightgoldenrodyellow'
        axfreq = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)



        #start value of slider
        startvalue = 0
        #slider with 3 graphs
        self.slider = Slider(
            ax=axfreq,
            label='Timeline',
            valmin=0,
            valmax=numGraphs-1,
            valinit=startvalue,
            valstep=1
        )
        self.slider.on_changed(self.update)

        #button
        axButtonL = plt.axes([0.25, 0.04, 0.04, 0.04], facecolor=axcolor)
        axButtonR = plt.axes([0.30, 0.04, 0.04, 0.04], facecolor=axcolor)
        buttonL = Button(axButtonL,'<',color = axcolor, hovercolor="b")
        buttonR = Button(axButtonR,'>',color = axcolor, hovercolor="b")

        buttonL.on_clicked(self.backward)
        buttonR.on_clicked(self.forward)

        # set timestamp as title
        plt.title(timestamp.strftime("%d/%m/%Y, %H:%M:%S"))

        plt.show()



    """
    Scale the weight values for the visualization 
    The weight values are always between ]0,1]
    """
    def scaleWeightValues(self,weights):
        scaledWeights = self.scaleBetweenValues(weights,1,10)
        return scaledWeights



    """
    Scale values between the ]lowerbound,upperbound] with the highest value projected to the upperbound
    @param weights : list of values to scale 
    @param lowerbound:  numerical int positive lower bound for the list of values 
    @param upperbound: numerical int positive upper bound for the list of values
    @return list of values scaled to ]lowerbound,upperbound]
    """
    def scaleBetweenValues(self,weights,lowerbound,upperbound):
        #scale for all graph snapshots, therefore take the max weight over all snapshots
        norm = [float(i)/self.temporalGraphMaxWeight for i in weights]
        norm = [(i*(upperbound-lowerbound))+lowerbound for i in norm]
        return norm


    #Round very small labels to the most significant digits
    def weightLabelRounding(self,weightLabels):
        weightValues = np.array(list(weightLabels.values()))


        round_it_np = np.vectorize(self.round_it)
        result = round_it_np(weightValues, 4)
        labelValuesAsList = result.tolist()
        #pass these back into the weightLabels dict
        i = 0
        for key,value in weightLabels.items():
            weightLabels[key] = labelValuesAsList[i]
            i += 1

        return weightLabels


    def round_it(self, x, sig):
        return round(x, sig-int(floor(log10(abs(x))))-1)
