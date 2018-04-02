import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *
from TheFastAndTheFuriousLearnDTree import *

###############################################
#This code was created by Billy Davis (wgd33), Morey Wood (wmw100), and Marcus Brumfield (mib21)
#   for Programming Assignment 3: RISK for CSE 6633 Artificial Intelligence
#   Decemeber 1, 2015
###############################################


dTreeKing = None

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    global dTreeKing
    
    if dTreeKing is None:
        print 'Loading DTree'
        dTreeKing = loadDTree('TheFastAndFuriousTokyo.dtree')
        print 'Done.'
    #Get the possible actions in this state
    actions = getAllowedActions(state)
    realCurrentPlayer = state.current_player
    turnType = state.turn_type
    # print 'Heuristic AI : Player', state.players[state.current_player].name, 'considering', len(actions), 'actions'


    #To keep track of the best action we find
    best_action = None
    best_action_value = None
    actionValues = []

    #modifiyed from our groups Homefront AI
    if turnType == "Fortify":
        possible_actions = []
        frontier_reinforcenemnt = []
        frontier_adjacent = []
        frontier = get_frontier(state, realCurrentPlayer)
        for a in actions:
            if a.to_territory is not None:
                to_territory_id = state.board.territory_to_id[a.to_territory]
                if to_territory_id in frontier:
                    frontier_reinforcenemnt.append(a)
                    continue
                for each_neighbor in state.board.territories[to_territory_id].neighbors:

                    if each_neighbor in frontier:
                        frontier_adjacent.append(a)
                        break
                for n in state.board.territories[to_territory_id].neighbors:
                    if state.owners[n] != state.current_player:
                        possible_actions.append(a)
        if len(frontier_reinforcenemnt) > 0:
            actions = frontier_reinforcenemnt
        elif len(frontier_adjacent) > 0:
            actions = frontier_adjacent

    if state.turn_type == 'PreAssign' and len(state.players)==2:
        return pickAssign(state, actions)

    #Evaluate each action
    for a in actions:
        #Simulate the action, get all possible successors
        successors, probabilities = simulateAction(state, a)

        #Compute the expected heuristic value of the successors
        current_action_value = 0.0
        
        for i in range(len(successors)):
            #Each successor contributes its heuristic value * its probability to this action's value
            # current_action_value += (heuristicOriginal(successors[i],realCurrentPlayer) * probabilities[i])
            
            #this is the turnType stuff
            #   PreAssign, PrePlace, Place, TurnInCards, Attack, Occupy, Fortify, GameOver
            if turnType == "PreAssign":
                current_action_value += (heuristicPreAssign(successors[i],realCurrentPlayer) * probabilities[i])
            elif turnType == "Preplace" or turnType == "Place" or  turnType == "Occupy" or turnType == "Fortify" :
                current_action_value += (heuristicPreplace(successors[i],realCurrentPlayer) * probabilities[i])
            elif turnType == "TurnInCards":
                current_action_value += (heuristicTurnInCards(successors[i],realCurrentPlayer) * probabilities[i])
            elif turnType == "Attack":
                if (state.owners.count(realCurrentPlayer) >= 35) or (len(getFronts(state, realCurrentPlayer)) < 4):
                    return actions[0]
                current_action_value += (heuristicAttack(successors[i],realCurrentPlayer) * probabilities[i])
            elif turnType == "GameOver":
                current_action_value += (heuristicGameOver(successors[i],realCurrentPlayer) * probabilities[i])
            else:
                current_action_value += (heuristicOriginal(successors[i],realCurrentPlayer) * probabilities[i])

        #Store this as the best action if it is the first or better than what we have found
        if best_action_value is None or current_action_value > best_action_value:
            best_action = a
            best_action_value = current_action_value
        actionValues.append(current_action_value)

    #Return the best action
    return best_action


def pickAssign(state, actions):
    #Set up the data instance to pass into the decision tree
    #Are we the first player?
    first_player = 0
    if state.current_player == 0:
        first_player = 1
        
    owners = state.owners[:]
    for t in range(len(owners)):
        if owners[t] == state.current_player:
            owners[t] = 1
        elif owners[t] is not None:
            owners[t] = 0
            
    owners.insert(0,first_player)
    
    best_v = -1
    best_a = None
    
    for a in actions:
        instance = owners[:]
        instance[state.board.territory_to_id[a.to_territory]+1] = 1
        av = evaluateAssignAction(instance, a)
        if av > best_v:
            best_v = av
            best_a = a
    
    return best_a
    
def evaluateAssignAction(instance, action):
    #Randomly complete the rest of the instance
    snones = []
    
    for t in range(len(instance)):
        if instance[t] is None:
            snones.append(t)
    
    num_samples = 100
    action_value = 0
    
    for s in range(num_samples):
        new_owner = 0
        nones = snones[:]
    
        while len(nones) > 0:
            #print 'HOWDY!'
            nt = random.choice(nones)
            nones.remove(nt)
            instance[nt] = new_owner
            if new_owner == 0:
                new_owner = 1
            else:
                new_owner = 0
    
        #Randomly filled out instance, evaluate
        action_value  += dTreeKing.get_prob_of_win(instance)
    
    return float(action_value) / float(num_samples)


#from Homefront
def get_territories(state, player):
    territories = []
    for each_territory in state.board.territories:
        if state.owners[each_territory.id] == player:
            territories.append(each_territory)
    return territories

#from Homefront
def get_frontier(state, player):
    frontier = []
    for each_territory in get_territories(state, player):
        for each_neighbor in each_territory.neighbors:
            if state.owners[each_neighbor] != player:
                frontier.append(each_neighbor)
    return frontier


#returns how many of your territories are in contact with the enemy
def totalFrontCalc(state, realCurrentPlayer):
    player = realCurrentPlayer
    total = 0
    for each in state.board.territories:
        if state.owners[each.id] != player:
            continue
        if not [i for i in each.neighbors if state.owners[i] == player]:
            total += 1
    return total

#Pressure from enemies on all of my territory
def enemyTotalPressureOnMe(state, realCurrentPlayer):
    player = realCurrentPlayer
    total = 0
    for each in state.board.territories:
        if state.owners[each.id] == player:
            total += sum([state.armies[i] for i in each.neighbors if state.owners[i] != player])
    return total

#Pressure from me onto my enemies
def myTotalPressureOnEnemy(state, realCurrentPlayer):
    player = realCurrentPlayer
    total = 0
    for each in state.board.territories:
        if state.owners[each.id] != player:
            total += sum([state.armies[i] for i in each.neighbors if state.owners[i] == player])
    return total

#The number of continents I own, a whole number for each I own and the highest percentage of the territories on a continent I don't own
def numConIOwn(state, realCurrentPlayer):
    player = realCurrentPlayer
    maxOwned = 0.0
    total = 0.0
    for n,c in state.board.continents.iteritems():
        terrOnConCount = 0.0
        for each in c.territories:
            if state.owners[each] == player:
                terrOnConCount += 1.0
        conOwnedFrac = terrOnConCount / len(c.territories)
        if conOwnedFrac == 1:
            total += 1
        else:
            maxOwned = max(maxOwned, conOwnedFrac)

    return total + maxOwned

#The number of continents I own, a whole number for each I own and the highest percentage of the territories on a continent I don't own
#   weighted based off the reward fsr controlling it
def numConIOwnWeightedReward(state, borderWeight, realCurrentPlayer):
    player = state.current_player
    maxOwned = 0.0
    total = 0.0
    for n,c in state.board.continents.iteritems():
        reward = c.reward
        terrOnConCount = 0.0
        for each in c.territories:
            if state.owners[each] == player:
                terrOnConCount += 1.0
            for i in (state.board.territories[each]).neighbors:
                if c.territories.count(i) == 0:
                    reward += borderWeight
                    continue
        conOwnedFrac = terrOnConCount / len(c.territories)
        if conOwnedFrac == 1:
            total += reward
        else:
            maxOwned = max(maxOwned, conOwnedFrac*reward)

    return (total + maxOwned)

#The number of continents a player owns
def numConPlayerOwn(state, player):
    maxOwned = 0.0
    total = 0.0
    for n,c in state.board.continents.iteritems():
        terrOnConCount = 0.0
        for each in c.territories:
            if state.owners[each] == player:
                terrOnConCount += 1.0
        conOwnedFrac = terrOnConCount / len(c.territories)
        total += conOwnedFrac

    return total# + maxOwned

#The max number of continents an enemy owns
def numConEnemyOwn(state, me):
    numCon_list = []
    for each in state.players:
        if each.id != me:
            numCon_list.append(numConPlayerOwn(state, each.id))
    return sum(numCon_list)

#returns the territories of player that are fronts
def getFronts(state, realCurrentPlayer):
    player = realCurrentPlayer
    fronts = []
    for each in state.board.territories:
        if state.owners[each.id] != player:
            continue
        elif not [i for i in each.neighbors if state.owners[i] != player]:
            fronts.append(each.id)
    return fronts

#Analyzes the fronts and returns the highest ratio, average ratio, and the minimum ratio, and the number at minimmum
#   ratios are mine to theirs
def frontArmyRatios(state, realCurrentPlayer):
    player = realCurrentPlayer
    frontRatios = []
    frontRatios12All = []
    frontRatiosA2A = []
    for each in state.board.territories:
        if state.owners[each.id] == player:
            mine = state.armies[each.id]
            mine += 0.0
            theirs = [state.armies[i] for i in each.neighbors if state.owners[i] != player]
            # theirs = [sum([state.armies[i] for i in each.neighbors if state.owners[i] != player])]
            for i in theirs:
                if i != 0:
                    frontRatios.append(mine/i)
    mAx = 0
    mIn = 3000000
    average = 0.0
    for each in frontRatios:
        mIn = min(each, mIn)
        mAx = max(each,mAx)
        average += each
    if len(frontRatios) != 0:
        average = average/len(frontRatios)
    
    return mAx, average, mIn, frontRatios.count(mIn)

#Analyzes the fronts and returns the highest ratio, average ratio, and the minimum ratio, and the number at minimmum
#   ratios are mine to theirs, in the order of 1-to-1, 1-to-allEnemy, mineAdj-to-allEnemy
def frontArmyRatios3(state, realCurrentPlayer):
    player = realCurrentPlayer
    frontRatios = []
    frontRatios12All = []
    frontRatiosA2A = []
    for each in state.board.territories:
        if state.owners[each.id] == player:
            mine = state.armies[each.id]
            mine += 0.0
            theirs = [state.armies[i] for i in each.neighbors if state.owners[i] != player]
            theirSum = sum(theirs)
            mineAll = mine + sum([state.armies[i] for i in each.neighbors if state.owners[i] == player])
            for i in theirs:
                if i != 0:
                    frontRatios.append(mine/i)
            if theirSum != 0:
                frontRatios12All.append(mine/theirSum)
            if theirSum != 0:
                frontRatiosA2A.append(mineAll/theirSum)

    mAx = 0
    mIn = 3000000
    average = 0.0
    for each in frontRatios:
        mIn = min(each, mIn)
        mAx = max(each,mAx)
        average += each
    if len(frontRatios) != 0:
        average = average/len(frontRatios)
    
    max12A = max(frontRatios12All)
    min12A = min(frontRatios12All)
    avg12A = float(sum(frontRatios12All))/len(frontRatios12All) if len(frontRatios12All) > 0 else 0

    maxA2A = max(frontRatiosA2A)
    minA2A = min(frontRatiosA2A)
    avgA2A = float(sum(frontRatiosA2A))/len(frontRatiosA2A) if len(frontRatiosA2A) > 0 else 0

    return (mAx, average, mIn, frontRatios.count(mIn)), (max12A, min12A, avg12A, frontRatios12All.count(min12A)), (maxA2A, minA2A, avgA2A, frontRatiosA2A.count(minA2A))




#returns the number of disconnected graphs my territory is
def disconnectedMe(state, realCurrentPlayer):
    player = realCurrentPlayer
    myTerrUnchecked = []
    reachedNeighbors = []
    expandedNeighbors = []
    currentToCheck = None
    numberOfGraphs = 0
    for each in state.board.territories:
        if state.owners[each.id] == player:
            myTerrUnchecked.append(each.id)
    
    while (len(myTerrUnchecked) + len(reachedNeighbors))>0:
        currentToCheck = None
        if len(reachedNeighbors) > 0:
            currentToCheck = state.board.territories[reachedNeighbors.pop()]
        elif currentToCheck == None:
            currentToCheck = state.board.territories[myTerrUnchecked.pop()]
            numberOfGraphs += 1
        
        for each in currentToCheck.neighbors:
            if state.owners[each] != player:
                continue
            if myTerrUnchecked.count(each) > 0:
                myTerrUnchecked.remove(each)
            if (expandedNeighbors.count(each) == 0) and (reachedNeighbors.count(each) == 0):
                reachedNeighbors.append(each)

        expandedNeighbors.append(currentToCheck.id)

    return (numberOfGraphs-1)

def disconnectedEnemy(state, me):
    numGraphs_list = []
    for each in state.players:
        if each.id != me:
            numGraphs_list.append(disconnectedPlayer(state, each.id))
    return sum(numGraphs_list)

#returns the number of disconnected graphs of player's territory
def disconnectedPlayer(state, player):
    myTerrUnchecked = []
    reachedNeighbors = []
    expandedNeighbors = []
    currentToCheck = None
    numberOfGraphs = 0
    for each in state.board.territories:
        if state.owners[each.id] == player:
            myTerrUnchecked.append(each.id)
    
    while (len(myTerrUnchecked) + len(reachedNeighbors))>0:
        currentToCheck = None
        if len(reachedNeighbors) > 0:
            currentToCheck = state.board.territories[reachedNeighbors.pop()]
        elif currentToCheck == None:
            currentToCheck = state.board.territories[myTerrUnchecked.pop()]
            numberOfGraphs += 1
        
        for each in currentToCheck.neighbors:
            if state.owners[each] != player:
                continue
            if myTerrUnchecked.count(each) > 0:
                myTerrUnchecked.remove(each)
            if (expandedNeighbors.count(each) == 0) and (reachedNeighbors.count(each) == 0):
                reachedNeighbors.append(each)

        expandedNeighbors.append(currentToCheck.id)

    return (numberOfGraphs-1)


#returns the highest armies*valueofgraph for each graph
#   possibly change to account for connenient value
def maxArmyGraph(state, realCurrentPlayer):
    player = realCurrentPlayer
    myTerrUnchecked = []
    reachedNeighbors = []
    expandedNeighbors = []
    currentToCheck = None
    numberOfGraphs = 0
    for each in state.board.territories:
        if state.owners[each.id] == player:
            myTerrUnchecked.append(each.id)

    terrThisGraph = 0
    armiesThisGraph = 0
    maxArmyTerrGraph = 0
    
    while (len(myTerrUnchecked) + len(reachedNeighbors))>0:
        currentToCheck = None
        if len(reachedNeighbors) > 0:
            currentToCheck = state.board.territories[reachedNeighbors.pop()]
        elif currentToCheck == None:
            currentToCheck = state.board.territories[myTerrUnchecked.pop()]
            numberOfGraphs += 1
            maxArmyTerrGraph = max(maxArmyTerrGraph, armiesThisGraph*terrThisGraph)
            terrThisGraph = 0
            armiesThisGraph = 0
        
        for each in currentToCheck.neighbors:
            if state.owners[each] != player:
                continue
            if myTerrUnchecked.count(each) > 0:
                myTerrUnchecked.remove(each)
            if (expandedNeighbors.count(each) == 0) and (reachedNeighbors.count(each) == 0):
                reachedNeighbors.append(each)
                terrThisGraph += 1
                armiesThisGraph += state.armies[each]

        expandedNeighbors.append(currentToCheck.id)

    return maxArmyTerrGraph

#returns a tuple with the first being my armies and the second everyone elses'
def allArmies(state, realCurrentPlayer):
    me = realCurrentPlayer
    mine = 0
    theirs = 0
    for i in state.board.territories:
        if state.owners[i.id] == me:
            mine += state.armies[i.id]
        else:
            theirs += state.armies[i.id]
    return (mine, theirs)

#returns the strength of the weakest front territory for itself
def strengthWeakestFront(state, realCurrentPlayer):
    pl = realCurrentPlayer
    arms = 1000
    # for i in state.board.territories:
    for i in getFronts(state, pl):
        if state.owners[i]== pl:
            if state.armies[i] < arms:
                arms = state.armies[i]
    return arms

#returns the strength of the strongest front territory for itself
def strengthStrongestFront(state, realCurrentPlayer):
    pl = realCurrentPlayer
    arms = -1
    for i in state.board.territories:
        if state.owners[i.id] == pl:
            if state.armies[i.id] > arms:
                arms = state.armies[i.id]
    return arms

#sum of all territories adjacent to me, counting some double
def adjTerrNotMine(state, realCurrentPlayer):
    player = realCurrentPlayer
    total = 0
    for each in state.board.territories:
        if state.owners[each.id] == player:
            for i in each.neighbors:
                if state.owners[i] != player:
                    if state.owners[i] == None:
                        total -= 0.5 #count the empty ones only half as much
                    total += 1
    return total

def heuristicOriginal(state, realCurrentPlayer):
    """Returns a number telling how good this state is"""
    toBeReturned = 0

    totalFrontWeight = 0
    enemyPressureOnMeWeight = 0
    myArmyWeight = 2
    theirArmyWeight = -3
    myTotalPressureOnEnemyWeight = 0
    numConIOwnWeight = 50
    numConIOwnWeightedRewardWeight = 100
    borderWeight = -0.000007
    conquered_territoryWeight = 125
    strengthStrongestFrontWeight = -1
    strengthWeakestFrontWeight = 2
    disconnectedGraphsWeight = -100
    disconnectedEnemyWeight = 5
    numConEnemyOwnWeight = -5
    maxArmyGraphWeight = 12
    maxRatioWeight = 1
    avgRatioWeight = 10
    minRatioWeight = 2
    numAtMinWeight = -20


    (myArmy, theirArmy) = allArmies(state, realCurrentPlayer)
    maxRatio, avgRatio, minRatio, numAtMin = frontArmyRatios(state, realCurrentPlayer)

    toBeReturned += strengthStrongestFront(state, realCurrentPlayer) * strengthStrongestFrontWeight
    toBeReturned += strengthWeakestFront(state, realCurrentPlayer) * strengthWeakestFrontWeight
    toBeReturned += myArmyWeight * myArmy
    toBeReturned += theirArmyWeight * theirArmy
    toBeReturned += totalFrontWeight * totalFrontCalc(state, realCurrentPlayer)
    toBeReturned += enemyPressureOnMeWeight * enemyTotalPressureOnMe(state, realCurrentPlayer)
    toBeReturned += myTotalPressureOnEnemyWeight * myTotalPressureOnEnemy(state, realCurrentPlayer)
    toBeReturned += numConIOwnWeightedReward(state,borderWeight, realCurrentPlayer) * numConIOwnWeightedRewardWeight
    toBeReturned += numConIOwn(state, realCurrentPlayer) * numConIOwnWeight
    toBeReturned += numConEnemyOwnWeight * numConEnemyOwn(state, realCurrentPlayer)
    toBeReturned += state.players[realCurrentPlayer].conquered_territory * conquered_territoryWeight
    toBeReturned += disconnectedGraphsWeight * disconnectedMe(state, realCurrentPlayer)
    toBeReturned += disconnectedEnemyWeight * disconnectedEnemy(state, realCurrentPlayer)
    toBeReturned += maxArmyGraphWeight * maxArmyGraph(state, realCurrentPlayer)
    toBeReturned += maxRatio*maxRatioWeight
    toBeReturned += avgRatio*avgRatioWeight
    toBeReturned += minRatio*minRatioWeight
    toBeReturned += numAtMin*numAtMinWeight

    return toBeReturned

#PreAssign, PrePlace, Place, TurnInCards, Attack, Occupy, Fortify, GameOver
class PreAssignWeights():
    totalFrontWeight = 0
    enemyPressureOnMeWeight = -6
    myArmyWeight = 0
    theirArmyWeight = 0
    myTotalPressureOnEnemyWeight = 0
    numConIOwnWeight = 4
    numConIOwnWeightedRewardWeight = 9
    borderWeight = -0.000006
    conquered_territoryWeight = 0
    strengthStrongestFrontWeight = 0
    strengthWeakestFrontWeight = 0
    disconnectedGraphsWeight = -30
    disconnectedEnemyWeight = 0
    numConEnemyOwnWeight = 0
    maxArmyGraphWeight = 0
    maxRatioWeight = 0
    avgRatioWeight = 0
    minRatioWeight = 0
    numAtMinWeight = 0
    adjTerrNotMineWeight = -6

def heuristicPreAssign(state, realCurrentPlayer):
    """Returns a number telling how good this state is"""

    toBeReturned = 0

    (myArmy, theirArmy) = allArmies(state, realCurrentPlayer)
    maxRatio, avgRatio, minRatio, numAtMin = frontArmyRatios(state, realCurrentPlayer)

    toBeReturned += strengthStrongestFront(state, realCurrentPlayer) * PreAssignWeights.strengthStrongestFrontWeight
    toBeReturned += strengthWeakestFront(state, realCurrentPlayer) * PreAssignWeights.strengthWeakestFrontWeight
    toBeReturned += PreAssignWeights.myArmyWeight * myArmy
    toBeReturned += PreAssignWeights.theirArmyWeight * theirArmy
    toBeReturned += PreAssignWeights.totalFrontWeight * totalFrontCalc(state, realCurrentPlayer)
    toBeReturned += PreAssignWeights.enemyPressureOnMeWeight * enemyTotalPressureOnMe(state, realCurrentPlayer)
    toBeReturned += PreAssignWeights.myTotalPressureOnEnemyWeight * myTotalPressureOnEnemy(state, realCurrentPlayer)
    toBeReturned += numConIOwnWeightedReward(state, PreAssignWeights.borderWeight, realCurrentPlayer) * PreAssignWeights.numConIOwnWeightedRewardWeight
    toBeReturned += numConIOwn(state, realCurrentPlayer) * PreAssignWeights.numConIOwnWeight
    toBeReturned += PreAssignWeights.numConEnemyOwnWeight * numConEnemyOwn(state, realCurrentPlayer)
    toBeReturned += state.players[realCurrentPlayer].conquered_territory * PreAssignWeights.conquered_territoryWeight
    toBeReturned += PreAssignWeights.disconnectedGraphsWeight * disconnectedMe(state, realCurrentPlayer)
    toBeReturned += PreAssignWeights.disconnectedEnemyWeight * disconnectedEnemy(state, realCurrentPlayer)
    toBeReturned += PreAssignWeights.maxArmyGraphWeight * maxArmyGraph(state, realCurrentPlayer)
    toBeReturned += maxRatio*PreAssignWeights.maxRatioWeight
    toBeReturned += avgRatio*PreAssignWeights.avgRatioWeight
    toBeReturned += minRatio*PreAssignWeights.minRatioWeight
    toBeReturned += numAtMin*PreAssignWeights.numAtMinWeight
    toBeReturned += adjTerrNotMine(state, realCurrentPlayer)*PreAssignWeights.adjTerrNotMineWeight

    return toBeReturned

class PrePlaceWeights():
    totalFrontWeight = 0
    enemyPressureOnMeWeight = 0
    myArmyWeight = 2
    theirArmyWeight = -3
    myTotalPressureOnEnemyWeight = 15
    numConIOwnWeight = 0
    numConIOwnWeightedRewardWeight = 0
    borderWeight = -7e-06
    conquered_territoryWeight = 0
    strengthStrongestFrontWeight = -1
    strengthWeakestFrontWeight = 6
    disconnectedGraphsWeight = 0
    disconnectedEnemyWeight = 0
    numConEnemyOwnWeight = 0
    maxArmyGraphWeight = 10
    maxRatioWeight = 0
    avgRatioWeight = 4
    minRatioWeight = 2
    numAtMinWeight = -3
    maxRatioWeight12A = -1
    avgRatioWeight12A = 9
    minRatioWeight12A = 6
    numAtMinWeight12A = -7
    maxRatioWeightA2A = 1
    avgRatioWeightA2A = 1
    minRatioWeightA2A = 20
    numAtMinWeightA2A = -3


def heuristicPreplace(state, realCurrentPlayer):
    """Returns a number telling how good this state is"""
    toBeReturned = 0

    (myArmy, theirArmy) = allArmies(state, realCurrentPlayer)
    (maxRatio, avgRatio, minRatio, numAtMin), (maxRatio12A, avgRatio12A, minRatio12A, numAtMin12A), (maxRatioA2A, avgRatioA2A, minRatioA2A, numAtMinA2A) = frontArmyRatios3(state, realCurrentPlayer)

    toBeReturned += strengthStrongestFront(state, realCurrentPlayer) * PrePlaceWeights.strengthStrongestFrontWeight
    toBeReturned += strengthWeakestFront(state, realCurrentPlayer) * PrePlaceWeights.strengthWeakestFrontWeight
    toBeReturned += PrePlaceWeights.myArmyWeight * myArmy
    toBeReturned += PrePlaceWeights.theirArmyWeight * theirArmy
    toBeReturned += PrePlaceWeights.totalFrontWeight * totalFrontCalc(state, realCurrentPlayer)
    toBeReturned += PrePlaceWeights.enemyPressureOnMeWeight * enemyTotalPressureOnMe(state, realCurrentPlayer)
    toBeReturned += PrePlaceWeights.myTotalPressureOnEnemyWeight * myTotalPressureOnEnemy(state, realCurrentPlayer)

    toBeReturned += numConIOwnWeightedReward(state,PrePlaceWeights.borderWeight, realCurrentPlayer) * PrePlaceWeights.numConIOwnWeightedRewardWeight
    toBeReturned += numConIOwn(state, realCurrentPlayer) * PrePlaceWeights.numConIOwnWeight
    toBeReturned += PrePlaceWeights.numConEnemyOwnWeight * numConEnemyOwn(state, realCurrentPlayer)
    toBeReturned += state.players[realCurrentPlayer].conquered_territory * PrePlaceWeights.conquered_territoryWeight
    toBeReturned += PrePlaceWeights.disconnectedGraphsWeight * disconnectedMe(state, realCurrentPlayer)
    toBeReturned += PrePlaceWeights.disconnectedEnemyWeight * disconnectedEnemy(state, realCurrentPlayer)

    toBeReturned += PrePlaceWeights.maxArmyGraphWeight * maxArmyGraph(state, realCurrentPlayer)
    toBeReturned += maxRatio*PrePlaceWeights.maxRatioWeight
    toBeReturned += avgRatio*PrePlaceWeights.avgRatioWeight
    toBeReturned += minRatio*PrePlaceWeights.minRatioWeight
    toBeReturned += numAtMin*PrePlaceWeights.numAtMinWeight

    toBeReturned += PrePlaceWeights.maxRatioWeight12A*maxRatio12A
    toBeReturned += PrePlaceWeights.avgRatioWeight12A*avgRatio12A
    toBeReturned += PrePlaceWeights.minRatioWeight12A*minRatio12A
    toBeReturned += PrePlaceWeights.numAtMinWeight12A*numAtMin12A

    toBeReturned += PrePlaceWeights.maxRatioWeightA2A*maxRatioA2A
    toBeReturned += PrePlaceWeights.avgRatioWeightA2A*avgRatioA2A
    toBeReturned += PrePlaceWeights.minRatioWeightA2A*minRatioA2A
    toBeReturned += PrePlaceWeights.numAtMinWeightA2A*numAtMin

    if (maxRatio >= (20*minRatio) or (maxRatio > 50) or (minRatio > 40)):
        toBeReturned += -300

    return toBeReturned


def heuristicTurnInCards(state, realCurrentPlayer):
    """Returns a number telling how good this state is"""
    toBeReturned = 0

    totalFrontWeight = 0
    enemyPressureOnMeWeight = 0
    myArmyWeight = 2
    theirArmyWeight = -3
    myTotalPressureOnEnemyWeight = 0
    numConIOwnWeight = 50
    numConIOwnWeightedRewardWeight = 100
    borderWeight = -0.000007
    conquered_territoryWeight = 125
    strengthStrongestFrontWeight = -1
    strengthWeakestFrontWeight = 2
    disconnectedGraphsWeight = -100
    disconnectedEnemyWeight = 5 #without this, 2 wins and 4 ties out of 10
    numConEnemyOwnWeight = -5
    maxArmyGraphWeight = 12
    maxRatioWeight = 1
    avgRatioWeight = 10
    minRatioWeight = 2
    numAtMinWeight = -20


    (myArmy, theirArmy) = allArmies(state, realCurrentPlayer)
    maxRatio, avgRatio, minRatio, numAtMin = frontArmyRatios(state, realCurrentPlayer)

    toBeReturned += strengthStrongestFront(state, realCurrentPlayer) * strengthStrongestFrontWeight
    toBeReturned += strengthWeakestFront(state, realCurrentPlayer) * strengthWeakestFrontWeight
    toBeReturned += myArmyWeight * myArmy
    toBeReturned += theirArmyWeight * theirArmy
    toBeReturned += totalFrontWeight * totalFrontCalc(state, realCurrentPlayer)
    toBeReturned += enemyPressureOnMeWeight * enemyTotalPressureOnMe(state, realCurrentPlayer)
    toBeReturned += myTotalPressureOnEnemyWeight * myTotalPressureOnEnemy(state, realCurrentPlayer)
    toBeReturned += numConIOwnWeightedReward(state,borderWeight, realCurrentPlayer) * numConIOwnWeightedRewardWeight
    toBeReturned += numConIOwn(state, realCurrentPlayer) * numConIOwnWeight
    toBeReturned += numConEnemyOwnWeight * numConEnemyOwn(state, realCurrentPlayer)
    toBeReturned += state.players[realCurrentPlayer].conquered_territory * conquered_territoryWeight
    toBeReturned += disconnectedGraphsWeight * disconnectedMe(state, realCurrentPlayer)
    toBeReturned += disconnectedEnemyWeight * disconnectedEnemy(state, realCurrentPlayer)
    toBeReturned += maxArmyGraphWeight * maxArmyGraph(state, realCurrentPlayer)
    toBeReturned += maxRatio*maxRatioWeight
    toBeReturned += avgRatio*avgRatioWeight
    toBeReturned += minRatio*minRatioWeight
    toBeReturned += numAtMin*numAtMinWeight

    return toBeReturned

class AttackWeights():
    totalFrontWeight = 20
    enemyPressureOnMeWeight = 2.5
    myArmyWeight = 20
    theirArmyWeight = 0
    myTotalPressureOnEnemyWeight = 2
    numConIOwnWeight = 50
    numConIOwnWeightedRewardWeight = 100
    borderWeight = -7e-06
    conquered_territoryWeight = 200
    strengthStrongestFrontWeight = 0
    strengthWeakestFrontWeight = 2
    disconnectedGraphsWeight = -100
    disconnectedEnemyWeight = 5
    numConEnemyOwnWeight = -2
    maxArmyGraphWeight = 0
    maxRatioWeight = 2
    avgRatioWeight = 7
    minRatioWeight = 3
    numAtMinWeight = -3
    maxRatioWeight12A = 3
    avgRatioWeight12A = 10
    minRatioWeight12A = 3
    numAtMinWeight12A = -7
    maxRatioWeightA2A = 2
    avgRatioWeightA2A = 3
    minRatioWeightA2A = 5
    numAtMinWeightA2A = -4

def heuristicAttack(state, realCurrentPlayer):
    """Returns a number telling how good this state is"""

    toBeReturned = 0
    (myArmy, theirArmy) = allArmies(state, realCurrentPlayer)#
    (maxRatio, avgRatio, minRatio, numAtMin), (maxRatio12A, avgRatio12A, minRatio12A, numAtMin12A), (maxRatioA2A, avgRatioA2A, minRatioA2A, numAtMinA2A) = frontArmyRatios3(state, realCurrentPlayer)

    toBeReturned += strengthStrongestFront(state, realCurrentPlayer) * AttackWeights.strengthStrongestFrontWeight
    toBeReturned += strengthWeakestFront(state, realCurrentPlayer) * AttackWeights.strengthWeakestFrontWeight
    toBeReturned += AttackWeights.myArmyWeight * myArmy#
    toBeReturned += AttackWeights.theirArmyWeight * theirArmy#
    toBeReturned += AttackWeights.totalFrontWeight * totalFrontCalc(state, realCurrentPlayer)#
    toBeReturned += AttackWeights.enemyPressureOnMeWeight * enemyTotalPressureOnMe(state, realCurrentPlayer)
    toBeReturned += AttackWeights.myTotalPressureOnEnemyWeight * myTotalPressureOnEnemy(state, realCurrentPlayer)
    toBeReturned += numConIOwnWeightedReward(state,AttackWeights.borderWeight, realCurrentPlayer) * AttackWeights.numConIOwnWeightedRewardWeight
    toBeReturned += numConIOwn(state, realCurrentPlayer) * AttackWeights.numConIOwnWeight
    toBeReturned += AttackWeights.numConEnemyOwnWeight * numConEnemyOwn(state, realCurrentPlayer)
    toBeReturned += state.players[realCurrentPlayer].conquered_territory * AttackWeights.conquered_territoryWeight
    toBeReturned += AttackWeights.disconnectedGraphsWeight * disconnectedMe(state, realCurrentPlayer)
    toBeReturned += AttackWeights.disconnectedEnemyWeight * disconnectedEnemy(state, realCurrentPlayer)
    toBeReturned += AttackWeights.maxArmyGraphWeight * maxArmyGraph(state, realCurrentPlayer)#
    toBeReturned += AttackWeights.maxRatioWeight*maxRatio
    toBeReturned += AttackWeights.avgRatioWeight*avgRatio
    toBeReturned += AttackWeights.minRatioWeight*minRatio
    toBeReturned += AttackWeights.numAtMinWeight*numAtMin

    toBeReturned += AttackWeights.maxRatioWeight12A*maxRatio12A
    toBeReturned += AttackWeights.avgRatioWeight12A*avgRatio12A
    toBeReturned += AttackWeights.minRatioWeight12A*minRatio12A
    toBeReturned += AttackWeights.numAtMinWeight12A*numAtMin12A

    toBeReturned += AttackWeights.maxRatioWeightA2A*maxRatioA2A
    toBeReturned += AttackWeights.avgRatioWeightA2A*avgRatioA2A
    toBeReturned += AttackWeights.minRatioWeightA2A*minRatioA2A
    toBeReturned += AttackWeights.numAtMinWeightA2A*numAtMinA2A

    #stop where it gets stuck building an infinite army
    if minRatio >= 50:
        toBeReturned += -1000000000
    if (state.turn_type == "GameOver") and (state.current_player == realCurrentPlayer):
        toBeReturned = 100000000000000000000000000

    return toBeReturned


def heuristicGameOver(state, realCurrentPlayer):
    """Returns a number telling how good this state is"""
    toBeReturned = 0

    if (state.turn_type == "GameOver") and (state.current_player == realCurrentPlayer):
        toBeReturned = 1000000000000000

    return toBeReturned



#Stuff below this is just to interface with Risk.pyw GUI version
#DO NOT MODIFY
    
def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    print 'AI Wrapper created state. . . '
    game_state.print_state()
    action = getAction(game_state)
    return translateAction(game_state, action)
            
def Assignment(player):
#Need to Return the name of the chosen territory
    return aiWrapper('Assignment')
     
def Placement(player):
#Need to return the name of the chosen territory
     return aiWrapper('Placement')
    
def Attack(player):
 #Need to return the name of the attacking territory, then the name of the defender territory    
    return aiWrapper('Attack')

   
def Occupation(player,t1,t2):
 #Need to return the number of armies moving into new territory      
    occupying = [t1.name,t2.name]
    aiWrapper('Occupation',occupying)
   
def Fortification(player):
    return aiWrapper('Fortification')

  