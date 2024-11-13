import collections
import networkx as nx
import operator
import community as community_louvain
from networkx.algorithms.community import greedy_modularity_communities
"""for leiden"""
import igraph as ig
import leidenalg as la

"""
Detect communities in the graph 
@param graph a weighted networkx graph, weight attribute is called "weight"
@param previousPartition partition of the previous graph snapshot
@returns partition of the current snapshot as a dictionary with the nodes as keys and their communities as value
        membershipvector: if Leiden is used this is the partition in a Leiden compatible format 
                        otherwise this is None
"""
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

"""
@param graph  a weighted networkx graph, weight attribute is called "weight"
@param partition : partition of the previous graph snapshot
"""
def louvainCommunityDetection(graph, partition):
    #The order in which the nodes are considered can affect the final output. In the algorithm the ordering happens using a random shuffle
    #we set the seed for the random generator to be the same each time
    #Randomize Will randomize the node evaluation order and the community evaluation order to get different partitions at each call
    partition = community_louvain.best_partition(graph,weight="weight",partition=partition,randomize=True)

    #isolated nodes should be their own community
    partition = assignIsolatedNodesTheirOwnCommunity(graph, partition)

    return partition


"""
@param nodes: list of nodes IDs (keys) 
@param partition: partition dictionary with the nodes as keys and their communities as value
@return partition where new nodes (those in nodes but not in partition) are added each as their separate community  
"""
def processPreviousCommunityState(nodes, partition):
    #if there is no previous partition, return none
    if not partition:
        #no nodes and communities yet
        nodeIDs = []
        maxCommNumber = -1
        #empty dict
        partition = {}

    else:
        nodeIDs = list(partition.keys())
        #distinct community numbers
        communities = set(val for val in partition.values())
        maxCommNumber = max(communities)

    for node in nodes:
        if node not in nodeIDs:
            maxCommNumber = maxCommNumber +1
            partition[node] = maxCommNumber

    return partition





"""
Clauset Newman Moore community detection 
Deterministic community detection algorithm 
"""
def CNMcommunityDetection(g):
    partitionTransformed = {}
    #does not work for a graph without edges
    if g.number_of_edges() == 0:

        counter = 0
        #each node is its own community
        for node in g:
            partitionTransformed[node] = counter
            counter += 1
    else:
        partition = greedy_modularity_communities(g,weight="weight", resolution = 0.9)
        #transform to correct format

        counter = 0
        for set in partition:
            for node in set:
                partitionTransformed[node] = counter
            counter += 1

    return partitionTransformed


"""
Leiden community detection
"""
def leidenCommunityDetection(g,previousPartition):
    partitionTransformed = {}
    # transform to igraph
    h = ig.Graph.from_networkx(g)

    previousPartition = transformPreviousCommunityStateLeiden(previousPartition,h)

    # the weights attribute does not work for a graph without edges
    if g.number_of_edges() == 0:
        partition = la.find_partition(h, la.ModularityVertexPartition, initial_membership=previousPartition, n_iterations = -1, seed=123)
    else:
        partition = la.find_partition(h, la.ModularityVertexPartition,initial_membership=previousPartition,weights="weight",n_iterations = -1, seed=123)

    #transform into the right data format
    membershipVector = partition.membership
    clusterIDs = set(membershipVector)
    for id in clusterIDs:
        #all members with that clusterID
        members = partition.__getitem__(id)
        for m in members:
            partitionTransformed[h.vs[m]["_nx_name"]] = id

    # isolated nodes should be their own community
    partitionTransformed = assignIsolatedNodesTheirOwnCommunity(g, partitionTransformed)

    return partitionTransformed


"""
Transform the dict of the previous community to a list format compatible with Leiden community detection 

@param partition: partition dictionary with the node ID as key and community ID as label 
@param graph is the iGraph of the current snapshot
@returns list with the community IDs in the order of the nodes in the igraph
"""
def transformPreviousCommunityStateLeiden(partition, graph):
    # paste them into a list
    transformedPartition = []
    #number of nodes
    numberNodes = graph.vcount()
    for i in range(0, numberNodes):
        transformedPartition.append(partition[graph.vs[i]["_nx_name"]])


    return transformedPartition


"""
When previous community assignment is passed as the initial membership and a node loses all its connections it keeps the same community assignment as its initial membership
We want to assign each isolated node to their own community 
@param graph  a weighted networkx graph , weight attribute is called "weight"
@param partition : partition of the current snapshot as a dictionary with the nodes as keys and their communities as value
@return altered partition in which isolated nodes each are their own community
"""
def assignIsolatedNodesTheirOwnCommunity(graph, partition):
    #if node is isolated AND has other members in its community: change this node to its own community

    # distinct community numbers
    communities = set(val for val in partition.values())
    maxCommNumber = max(communities)

    #get node IDs that are isolated
    isolateNodeIDs = getIsolatedNodes(graph)
    for node in isolateNodeIDs:
        #check if there are other nodes it their community
        if getNumberOfNodesInCommunity(partition, partition[node]) > 1:
            maxCommNumber = maxCommNumber + 1
            #alter their current community number
            partition[node] = maxCommNumber

    return partition


"""
@param partition : partition of the current snapshot as a dictionary with the nodes as keys and their communities as value
@param communityNumber : ID of the community 
@return number of nodes with that community number 
"""
def getNumberOfNodesInCommunity(partition, communityNumber):
    number = operator.countOf(partition.values(),communityNumber)
    return number

"""

@param graph  a weighted networkx graph , weight attribute is called "weight"
@return list of all node IDs in the graph that are isolated, meaning they have no incident edges 
"""
def getIsolatedNodes(graph):
    isolates =  list(nx.isolates(graph))
    return isolates