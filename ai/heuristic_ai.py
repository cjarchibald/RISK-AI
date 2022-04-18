import random
from risktools import *
#For interacting with interactive GUI
from gui.aihelper import *
from gui.turbohelper import *

### HEURISTIC AI ####
# 
#  This is the beginning of an AI that will simulate all allowed actions, evaluate each possible resulting state 
#  with a heuristic function, and select the action that leads to the highest expected heuristic value. 
#  
#  To complete this AI, simply implement the "heuristic" function below, returning a real number for a given state

def getAction(state, time_left=None):
    """Main AI function.  It should return a valid AI action for this state."""
   
    #Get the possible actions in this state
    actions = getAllowedActions(state)
 
    # Execute each action and get expected heuristic value of resulting state 
    
    # To keep track of the best action we find
    best_action = None
    best_action_value = None
    
    #Evaluate each action
    for a in actions:
               
        #Simulate the action, get all possible successor states
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
    """Returns a number telling how good this state is. 
       Implement this function to have a heuristic ai. """
    return 0
    
#Code below this is the interface with Risk.pyw GUI version
#DO NOT MODIFY
    
def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    print('AI Wrapper created state. . . ')
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
    return aiWrapper('Occupation',occupying)
   
def Fortification(player):
    return aiWrapper('Fortification')

  