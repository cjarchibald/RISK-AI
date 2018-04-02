import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    #if time_left is not None:
        #Decide how much time to spend on this decision
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    print 'Heuristic AI : Player', state.players[state.current_player].name, 'considering', len(actions), 'actions'
    
    #To keep track of the best action we find
    best_action = None
    best_action_value = None
    
    #Evaluate each action
    for a in actions:
               
        #Simulate the action, get all possible successors
        successors, probabilities = simulateAction(state, a)
              
        #Compute the expected heuristic value of the successors
        current_action_value = 0.0
        
        for i in range(len(successors)):
            #Each successor contributes its heuristic value * its probability to this action's value
            current_action_value += (heuristic(successors[i]) * probabilities[i])
        
        #Store this as the best action if it is the first or better than what we have found
        if best_action_value is None or current_action_value > best_action_value:
            best_action = a
            best_action_value = current_action_value
        
    #Return the best action
    return best_action

def heuristic(state):
    """Returns a number telling how good this state is"""
    return 0
    
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

  