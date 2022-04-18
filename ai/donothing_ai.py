import random
from risktools import *
#For interacting with interactive GUI
from gui.aihelper import *
from gui.turbohelper import *

### DO NOTHING AI ####
# 
#  This AI never attacks, and otherwise will choose a random action
#  This results in an AI that builds up strength, but can't win.  
#  To beat this agent requires attacking, so it is good to test with. 


def getAction(state, time_left=None):
    """Main AI function.  It should return a valid AI action for this state."""

    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    #Select random action (to use for non-attack turn types)    
    myaction = random.choice(actions)
    
    #If turn type is attack, then choose to end attack
    if state.turn_type == 'Attack':
        myaction = actions[-1] #The last action is always "Stop Attacking"
        
    return myaction

#Code below this is the interface with Risk.pyw GUI version
#DO NOT MODIFY
    
def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
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

  