import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    territory_values = {}
    continentRewards_v_territories = []
    contCount = 0
    for key in state.board.continents:
        continent = state.board.continents[key]
        #print(continent.name)
        value = continent.reward
        #print(value)
        sizer = len(continent.territories)
        #print(sizer)
        terrVal = 9-sizer
        continentRewards_v_territories.append([value, continent.territories])
        if terrVal < 1:
            terrVal = 1
        else:
            terrVal += 1

        for tID in continent.territories:
            territory_values[tID] = terrVal
      
    #if time_left is not None:
        #Decide how much time to spend on this decision
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    #print 'Heuristic AI : Player', state.players[state.current_player].name, 'considering', len(actions), 'actions'
    
    #To keep track of the best action we find
    best_action = None
    best_action_value = None
    actionType = state.turn_type
    
    #Evaluate each action
    for a in actions:
               
        #Simulate the action, get all possible successors
        successors, probabilities = simulateAction(state, a)
              
        #Compute the expected heuristic value of the successors
        current_action_value = 0.0
        
        for i in range(len(successors)):
            #Each successor contributes its heuristic value * its probability to this action's value
            current_action_value += (heuristic(successors[i], territory_values, continentRewards_v_territories, actionType, a) * probabilities[i])
        
        #Store this as the best action if it is the first or better than what we have found
        if best_action_value is None or current_action_value > best_action_value:
            best_action = a
            best_action_value = current_action_value
        
    #Return the best action
    return best_action

def heuristic(state, territory_values, continentRewards_v_territories, actionType, action):
    #territory_values, dict of territoryID:territoryValue
    #continentRewards_v_territories, list of [[contValue, [territoriesInCont]],...]
    #actionType is a string with the type of turn got us to this state
    heuristic = 0

    #make it attack spaces with no enemy neighbors first
    if actionType == "Attack":
        heuristic = 1

    #will turn in as many cards as possible
    elif actionType == "TurnInCards":
        for play in state.players:
            if play.id == state.current_player:
                heuristic += (5-len(play.cards))

    #will prioritize smaller continents during territory assignment
    elif actionType == "PreAssign":
        #print(territory_values[state.board.territory_to_id[action.to_territory]])
        heuristic += territory_values[state.board.territory_to_id[action.to_territory]]

    #will find which territory has more troops in the neighboring 
    elif actionType == "Occupy":
        origin = state.board.territories[state.board.territory_to_id[action.from_territory]]
        target = state.board.territories[state.board.territory_to_id[action.to_territory]]
        
        originEnemyNeighbors = 0
        for terrs in origin.neighbors:
            if state.owners[terrs] != state.current_player:
                originEnemyNeighbors += state.armies[terrs]
                
        targetEnemyNeighbors = 0
        for terrs in target.neighbors:
            if state.owners[terrs] != state.current_player:
                targetEnemyNeighbors += state.armies[terrs]

        
        heuristic += state.armies[origin.id] * originEnemyNeighbors
        heuristic += state.armies[target.id] * targetEnemyNeighbors

    #prioritizes border territories, particularly those in small continents that you control
    #or those next to territories in small continents that you control
    elif actionType == "Place" or actionType == "Fortify":
        count = 0
        myTerritories = []
        for terr in state.owners:
            if terr == state.current_player:
                myTerritories.append(count)
            count += 1
            
        #add troops in a territory up to the amount of neighboring enemy troops+2
        neighborTerrDict = {}
        targetNeighbors = 0
        for terr in myTerritories:
            neighborNumb = 0
            neighborTerr = 0
            for neighbors in state.board.territories[terr].neighbors:
                if state.owners[neighbors] != state.current_player:
                    neighborNumb += state.armies[neighbors]
                    neighborTerr += 1
            heuristic += 3*(neighborNumb - abs(neighborNumb - (state.armies[terr]-2)))
            neighborTerrDict[terr] = neighborTerr
            if action.to_territory != None:
                if state.board.territory_to_id[action.to_territory] == terr:
                    targetNeighbors = neighborTerr

            else:
                targetNeighbors = -1


        #if no neighboring territories, set to 0
        #print(targetNeighbors)
        if targetNeighbors > 0:
            #print(heuristic)
            heuristic += int(territory_values[state.board.territory_to_id[action.to_territory]]/2)
        elif targetNeighbors == 0:
            heuristic = -100000
        #print(heuristic)

    elif actionType == "PrePlace":
        count = 0
        current_player = state.owners[state.board.territory_to_id[action.to_territory]]
        myTerritories = []
        
        for terr in state.owners:
            if terr == current_player:
                myTerritories.append(count)
            count += 1
        #print(actionType)
        #print(state.current_player)
        neighborTerrDict = {}
        for terr in myTerritories:
            neighborNumb = 0
            neighborTerr = 0
            for neighbors in state.board.territories[terr].neighbors:
                if state.owners[neighbors] != current_player:
                    neighborNumb += state.armies[neighbors]
                    neighborTerr += 1
            heuristic += 3*(neighborNumb - abs(neighborNumb - (state.armies[terr])))
            neighborTerrDict[terr] = neighborTerr
            if action.to_territory != None:
                if state.board.territory_to_id[action.to_territory] == terr:
                    targetNeighbors = neighborTerr

            else:
                targetNeighbors = -1


        #if no neighboring territories, set to 0
        #print(targetNeighbors)
        if targetNeighbors > 0:
            #print(heuristic)
            heuristic += int(territory_values[state.board.territory_to_id[action.to_territory]]/2)
        elif targetNeighbors == 0:
            heuristic = -100000
        #print(heuristic)
        
        
    """Returns a number telling how good this state is"""
    return heuristic
    
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

  
