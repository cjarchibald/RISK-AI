import riskengine
import riskgui
import random
from aihelper import *
from turbohelper import *
from risktools import *
import sys
import os

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
        
    #Select a Random Action
    myaction = random.choice(actions)
    
    if state.turn_type == 'Attack':
        myaction = actions[0]
    
    if state.turn_type == 'Place' or state.turn_type == 'Fortify' or state.turn_type == 'PrePlace':
        possible_actions = []

        for a in actions:
            if a.to_territory is not None:
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        possible_actions.append(a)
                    
        if len(possible_actions) > 0:
            myaction = random.choice(possible_actions)
            
    if state.turn_type == 'PreAssign':
        # look for Chile
        for a in actions:
            if a.to_territory == 'Chile':
                myaction = a
                #print myaction.description()
                return myaction
        # look for South Africa
        for a in actions:
            if a.to_territory == 'South Africa':
                myaction = a
                #print myaction.description()
                return myaction
        
        # return owned territories' neighbors
        my_territories = []
        count = 0
        for b in state.owners:  # list of territories and their owners
            if b == state.current_player:
                my_territories.append(count)
            count += 1
        for a in actions:
            for c in my_territories:
                for d in state.board.territories[c].neighbors:
                    if state.board.territories[d].name == a.to_territory:
                        myaction = a
                        #print myaction.description()
                        return myaction
                
                    
        #print myaction.description()
                    
    return myaction


#Stuff below this is just to interface with Risk.pyw GUI version
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
    aiWrapper('Occupation',occupying)
   
def Fortification(player):
    return aiWrapper('Fortification')

  
