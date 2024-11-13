#code to match teams between 2 graph snapshots
import copy

"""
    Compare the previous graph snapshot with the current 
    Find the best matches between the teams in the previousGraph and in graph 
    @param previousGraph Graph object representing the first snapshot 
    @param graph Graph object representing the second snapshot 
    @return list of tuples where the first element of the tuple is a set of node IDs that represent a team in the first snapshot 
            and the second element a set of node IDs representing the same team in the second snapshot 
            Best match is based on most elements in common 
"""
def matchTeamsBetweenSnapshots(previousGraph, graph):
    #return dict with key is Node ID and value is community ID
    previousTeams = previousGraph.getTeams()
    currentTeams = graph.getTeams()
    #transform into list of teams
    previousTeamsList = transFormIntoSet(previousTeams)
    currentTeamsList = transFormIntoSet(currentTeams)

    #match teams: tuples of a team of the previous list and a team of the current list (or None if no match)
    teamMatches = findBestTeamMatches(previousTeamsList,currentTeamsList)

    return teamMatches




"""
    @communityDict: dict with nodeID as key and team number as value 
    @return list of sets: where each set consists of nodeIDs that belong to the same community 
"""
def transFormIntoSet(communityDict):
    teamList = []
    communities = set(val for val in communityDict.values())
    for team in communities:
        #get all nodes that belong to the team
        teamList.append(set([nodeID for nodeID, teamID in communityDict.items() if teamID == team]))
    return teamList


"""
    Pair communities : match the communities of previousTeams with the best matching communities in currentTeams 
    Based on how many nodes are the same 
    @param previousTeams : list of sets where each set contains node IDs that belong to the same team
    @param currentTeams: list of sets where each set contains node IDs that belong to the same team
    @return list of tuples with the first element being the team in the previous snapshot, and the second element being the team in the current snapshot 
    if a previous team or a current team has no match, the other element will be None 
"""
def findBestTeamMatches(previousTeams, currentTeams):
    matches = []
    #deep copy
    previousTeamsCopy = copy.deepcopy(previousTeams)
    currentTeamsCopy = copy.deepcopy(currentTeams)

    recalculate = True

    while recalculate:
        teamMatchDict = {}
        for team in previousTeamsCopy:
            bestMatch, numberOfMatchinItems = findBestMatchInList(team,currentTeamsCopy)
            #if bestMatch is not None
            if bestMatch:
                #hash needs to be frozenset
                teamMatchDict[frozenset(team)] = (bestMatch,numberOfMatchinItems)

        recalculate = False
        #repeat until no two teams have the same bestMatch
        for team, matchInfo in teamMatchDict.items():
        # check if another team has the same match
            teamList = findTeamsWithThisMatch(matchInfo[0],teamMatchDict)
            #if there are multiple teams, resolve this
            if len(teamList) > 1:
                #the most matching one
                bestMatchingTeam = max(teamList, key=teamList.get)
                #tuple of previousteam and currentteam: convert previousteam from frozenset back to set
                matches.append((set(bestMatchingTeam),matchInfo[0]))
                #both need to be taken out of the dict and it needs to be run again

                previousTeamsCopy.remove(bestMatchingTeam)
                currentTeamsCopy.remove(matchInfo[0])
                recalculate = True
                break
            #if there aren't we break from the while loop and do not recalculate

    #the teamMatchDict does not contain duplicate matches anymore
    #process the matches still in this dict
    for team, matchInfo in teamMatchDict.items():
        #the match can be a set or None if there is no match
        matches.append((set(team),matchInfo[0]))
        previousTeamsCopy.remove(team)
        currentTeamsCopy.remove(matchInfo[0])
    ################
    #there may be teams left from the current team list and previous team list that do not have a match , add these
    for team in currentTeamsCopy:
        #add to the list without a match
        matches.append((None,team))
    for team in previousTeamsCopy:
        #add to the list without a match
        matches.append((team, None))

    return matches


"""
    Find the keys where the [O] of the value is match
    @param match set of nodeIDs that form a team
    @param teamDict dictionary with set of node IDs as key, and as value a tuple (set of node IDs, number of equivalent nodes between key and value) 
    @return dictionary with team as key and number of equivalent nodes as value 
"""
def findTeamsWithThisMatch( match,teamDict):
    results = {}
    for team, matchInfo in teamDict.items():

        if matchInfo[0] == match:
            results[team] = matchInfo[1]
    return results



"""
    @param team list of nodeIDs
    @param teamList list of list where each list consists of nodeIDS that represent a team 
    @return the best matching team from teamList or None ; based on the number of equivalent node IDs
"""
def findBestMatchInList(team, teamList):
    bestMatch = None
    numberOfMatchingItems = 0
    for item in teamList:
        intersect = list(set(team) & set(item))

        if (len(intersect)) > numberOfMatchingItems:
            bestMatch = item
            numberOfMatchingItems = len(intersect)

    return bestMatch,numberOfMatchingItems

