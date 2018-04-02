import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    global actionCount,has_enemy
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)

    global playerId

    if state.turn_type == "Attack":
        return actions[0]
    elif state.turn_type == "Occupy":
        return actions[len(actions)-1]
    elif state.turn_type == "Fortify": 
        #only if there is no possiblity to fortify
        if len(actions) == 1:
            return actions[0]
        
        #move armies from a territory whose neighbor is on the border to that border territory
        my_b_t = my_borders(state)
        my_in_t = my_interior_territories(state)
        my_action = actions[len(actions)-1]
        max_troops = my_action.troops
        for a in actions:
            for b in my_b_t:
                if a.to_territory == b.name:
                    for i in my_in_t:
                        if a.from_territory == i.name:                                
                            if a.troops > max_troops:
                                my_action = a
                                max_troops = a.troops
        if my_action.troops != 0:
            return my_action

        #collect moves involving territories not on the border
        my_interior = my_interior_territories(state)
        terr_most_troops = None
        most_troops = 0
        for t in my_interior:
            if state.armies[t.id] > most_troops:
                terr_most_troops = t
                most_troops = state.armies[t.id]-1

        rand_acts = []
        for a in actions:
            if a.from_territory == terr_most_troops.name and a.troops == most_troops:
                rand_acts.append(a)
                
        return random.choice(rand_acts)
                

            
    elif state.turn_type == "PreAssign" or state.turn_type == "PrePlace":
        playerId = state.current_player
        
        #To keep track of the best action we find
        best_action = None
        best_action_value = None

        # Get the turn type so we can apply the appropriate heuristic
        turnType = state.turn_type

        best_actions = []
        
        #Evaluate each action
        for a in actions:
            #Simulate the action, get all possible successors
            successors, probabilities = simulateAction(state, a)
                  
            #Compute the expected heuristic value of the successors
            current_action_value = 0.0
            
            for i in range(len(successors)):
                #Each successor contributes its heuristic value * its probability to this action's value
                current_action_value += (heuristic(successors[i], turnType) * probabilities[i])
            
            #Store this as the best action if it is the first or better than what we have found
            if best_action_value is None or current_action_value > best_action_value:
                best_action = a
                best_action_value = current_action_value
                best_actions = []

            #Keep a list of tied options
            if best_action_value == current_action_value:
                best_actions.append(a)

        #Pick an option randomly from the tied actions
        index = random.randint(1, len(best_actions))
        best_action = best_actions[index-1]
        #Return the best action
        return best_action
    
    else: #find a territory that borders an enemy and put troops there
       for a in actions:
           for t in state.board.territories:
               if t.name == a.to_territory:
                   if state.owners[t.id] == state.current_player:
                       has_e = False
                       for n in t.neighbors:
                           if state.owners[n] != state.current_player:
                               has_e = True
                       if has_e == True:
                            return a                                
    return random.choice(actions)

def heuristic(state, turnType):
    """Returns a number telling how good this state is"""
    #Each function decides which features to evaluate and returns their evaluation
    #In this version, only the PreAssign and PrePlace heuristics are used
    if turnType == 'PreAssign':
        return getPreAssignHeuristic(state)
    elif turnType == 'PrePlace':
        return getPrePlaceHeuristic(state)
    elif turnType == 'TurnInCards':
        return getTurnInCardsHeuristic(state)
    elif turnType == 'Place':
        return getPlaceHeuristic(state)
    elif turnType == 'Attack':
        return getAttackHeuristic(state)
    elif turnType == 'Occupy':
        return getOccupyHeuristic(state)
    elif turnType == 'Fortify':
        return getFortifyHeuristic(state)
    else:
        print "INVALID TURN_TYPE!!!"
    
    return 0

def getPreAssignHeuristic(state):
    #Try to get specific continents at the start. After these continents are taken it picks the first territory it sees
    myTerritories, count, maxNum = getTerritoriesInContinentById('Australia', state, playerId)
    value = 0
    #We try to value Australia more than the rest at this point
    if count == maxNum:
        #Add more to a state if we get the whole continent because that's very important
        value += count*5 + 100
    else:
        value += count*5

    myTerritories, count, maxNum = getTerritoriesInContinentById('S. America', state, playerId)
    if count == maxNum:
        value += count*3 + 100
    else:
        value += count*3
        
    return value

def getPrePlaceHeuristic(state):
    myContinents, count = getContinentsById(state, playerId)
    value = 0
    #We want to put our troops on the borders of any continents we own
    for continent in myContinents:
        myTerritories, num, max = getTerritoriesInContinentById(continent, state, playerId)
        for territory in myTerritories:
            if isContinentBorder(state, territory):
                value += getTroopsInTerritory(state, territory)
    #If we don't own a continent, try to get as many troops in our target continents as possible
    if count == 0:
        myTerritories, count, max = getTerritoriesInContinentById('Australia', state, playerId)
        for territory in myTerritories:
            value += getTroopsInTerritory(state, territory)
        myTerritories, count, max = getTerritoriesInContinentById('S. America', state, playerId)
        for territory in myTerritories:
            value += getTroopsInTerritory(state, territory)
    return value

def getPlaceHeuristic(state):
    return 0
def getTurnInCardsHeuristic(state):
    return 0
def getAttackHeuristic(state):
    return 0
def getOccupyHeuristic(state):
    return 0
def getFortifyHeuristic(state):
    return 0

""" ---------------- """
""" Helper Functions """
""" ---------------- """

# return value [0,1] for the fraction of territories the current player owns
def numOfOwnedTerritories(state):
    pid = state.current_player
    num_owned = 0
    for i in state.owners:
        if pid == i:
            num_owned += 1
    return num_owned

def getTerritoriesInContinentById(continent, state, myId):
    #Returns the amount of territories in a given continent that belong to the specified player ID
    mine = []
    territories = state.board.continents[continent].territories
    count = 0
    for tempId in territories:
        if state.owners[tempId] == myId:
            mine.append(tempId)
            count += 1
    # Returns list of territory IDs, count of the territories, and number of overall territories in continent
    return mine, count, len(territories)

def getTroopsInTerritory(state, territory):
    #Returns number of troops in the territory (by ID)
    return state.armies[territory]

def getContinentsById(state, myId):
    #Get the owner's continents by player ID (Returns a list of continent IDs)
    mine = []
    num = 0
    for continent, item in state.board.continents.items():
        myTerritories, count, max = getTerritoriesInContinentById(continent, state, myId)
        if count == max:
            mine.append(continent)
            num += 1
    return mine, num

def isContinentBorder(state, territory):
    #Returns whether or not the territory is on the border of a continent
    for terr in state.board.territories[territory].neighbors:
        if getContinentByTerritoryId(state, terr) != getContinentByTerritoryId(state, territory):
            return True
    return False

def getContinentByTerritoryId(state, myId):
    #Returns the continent to which the territory ID belongs
    for name, continent in state.board.continents.items():
        if myId in continent.territories:
            return name

# function that returns a list of territory objects owned by the current player
def my_territories(state):
    mine = []
    for t in state.board.territories:
        if state.owners[t.id] == state.current_player:
            mine.append(t)
    return mine

# a function that determines if a territory has a enemy territory as a neighbor
def has_enemy(state,t_id):
    onBorder = False
    for n in state.board.territories[t_id].neighbors:
        if state.owners[n] != state.current_player:
            onBorder = True
            break
    return onBorder

# function that returns a list of territory objects that border a enemy territory
def my_borders(state):
    border_terrs = []
    my_terrs = my_territories(state)
    if my_terrs != None:
        for t in my_terrs:
            if has_enemy(state, t.id):
                border_terrs.append(t)
    return border_terrs

# function that returns a list of territory objects that are not on the border
def my_interior_territories(state):
    terr = []
    myT = my_territories(state)
    myB = my_borders(state)
    if myT != None and myB != None:
        for t in my_territories(state):
            if t not in myB:
                terr.append(t)
    return terr

def territory_id_to_name(state,t_id):
    return state.board.territories[t_id].name

# determines if the attacking territory is on the border
def is_on_border(state,t_id):
    my_border_terr = my_borders(state)
    for t in my_border_terr:
        if t.id == t_id:
            return True
    return False

""" END Helper Functions """
    
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

  
