import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *

import khan.intelligence

# Construct an intelligence object to actually perform work
intelligence = khan.intelligence.Intelligence(time_limit=6000,
                                              action_limit=2500,
                                              weights_path="weights.txt",
                                              depth_limit=1)

def getAction(state, time_left=None):
    # All intelligence is actually in the Intelligence class
    best_action = intelligence.get_action(state)
    return best_action

# Wrapping functions for GUI, should not be modified

def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    print 'AI Wrapper created state. . . '
    game_state.print_state()
    action = getAction(game_state)
    return translateAction(game_state, action)
            
def Assignment(player):
    return aiWrapper('Assignment')
     
def Placement(player):
     return aiWrapper('Placement')
    
def Attack(player):
    return aiWrapper('Attack')

def Occupation(player,t1,t2):
    occupying = [t1.name,t2.name]
    aiWrapper('Occupation',occupying)
   
def Fortification(player):
    return aiWrapper('Fortification')
