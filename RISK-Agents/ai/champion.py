import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *

#This is the function implement to implement an AI.
#Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    #if time_left is not None:
        #Decide how much time to spend on this decision
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    #print 'Heuristic AI : Player', state.players[state.current_player].name, 'considering', len(actions), 'actions'
    
    #To keep track of the best action we find
    best_action = random.choice(actions)
    best_action_value = None

    if state.turn_type == 'Attack':
        possible_actions = []
        for a in actions:
            current_action_value = 0.0
            if (a.to_territory != None) and (a.from_territory != None):
                armies_in_state = state.armies[state.board.territory_to_id[a.from_territory]]
                armies_at_neighbor = state.armies[state.board.territory_to_id[a.to_territory]]
                if (armies_in_state - armies_at_neighbor) > 2:
                    current_action_value = armies_in_state - armies_at_neighbor
		if (best_action_value == None) or (current_action_value > best_action_value):
                    possible_actions = []
                    possible_actions.append(a)
                    #best_action = a
                    best_action_value = current_action_value
                elif (current_action_value == best_action_value):
                    possible_actions.append(a)
        if len(possible_actions) > 0:
            best_action = random.choice(possible_actions)

    if state.turn_type == 'Fortify':
        possible_actions = []
        for a in actions:
            if a.to_territory is not None:
                to_hostile = 0
                from_hostile  = 0
                current_action_value = 0.0
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        to_hostile += 1
                for n in state.board.territories[state.board.territory_to_id[a.from_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        from_hostile += 1
                troops = a.troops
                if from_hostile == 0:
                    current_action_value = troops
                    if to_hostile > 0:
                        current_action_value = 2 * troops
                if (best_action_value == None) or (current_action_value > best_action_value):
                    possible_actions = []
                    possible_actions.append(a)
                    #best_action = a
                    best_action_value = current_action_value
                elif (current_action_value == best_action_value):
                    possible_actions.append(a)
        if len(possible_actions) > 0:
            best_action = random.choice(possible_actions)

    if state.turn_type == 'Occupy':
        possible_actions = []
        for a in actions:
            if a.to_territory is not None:
                to_hostile = 0
                from_hostile  = 0
                troops = a.troops
                current_action_value = 0.0
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        to_hostile += 1
                if to_hostile != 0:
                    current_action_value = troops 
                if best_action_value is None or current_action_value > best_action_value:
                    possible_actions = []
                    possible_actions.append(a)
                    #best_action = a
                    best_action_value = current_action_value
                elif (current_action_value == best_action_value):
                    possible_actions.append(a)
        if len(possible_actions) > 0:
            best_action = random.choice(possible_actions)

    if state.turn_type == 'Place':
        possible_actions = []
        for a in actions:
            if a.to_territory is not None:
                to_hostile = 0
                current_action_value = 0.0
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        current_action_value += state.armies[n]
                if best_action_value is None or current_action_value > best_action_value:
                    possible_actions = []
                    possible_actions.append(a)
                    #best_action = a
                    best_action_value = current_action_value
                elif (current_action_value == best_action_value):
                    possible_actions.append(a)
        if len(possible_actions) > 0:
            best_action = random.choice(possible_actions)

##    if state.turn_type == 'PrePlace':
##        for a in actions:
##            if a.to_territory is not None:
##                to_hostile = 0
##                current_action_value = 0
##                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
##                    if state.owners[n] != state.current_player:
##                        current_action_value += state.armies[n]
##                if best_action_value is None or current_action_value > best_action_value:
##                    best_action = a
##                    best_action_value = current_action_value
                    
    return best_action

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

  
