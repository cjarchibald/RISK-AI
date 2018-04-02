import riskengine
import riskgui
import random
from aihelper import *
from turbohelper import *
from risktools import *

territoryPriority = ["Indonesia", "New Guinea", "Laos", "Western Australia", "Eastern Australia",\
    "Brazil", "Colombia", "Peru", "Chile", "Alaska", "Greenland", "Quebec", "Mexico", "NorthwestTerritories",\
    "British Columbia", "Ontario", "Western U.S.", "Eastern U.S.", "Western Africa", "Egypt", "Ethiopia",\
    "Madagascar", "Zaire", "South Africa", "India", "China", "Iceland", "Great Britain", "Sweden",\
    "Manchuria", "Japan", "Western Europe", "Central Europe", "Ukraine", "Pakistan", "Middle East",\
    "Southern Europe", "Russia", "Siberia", "Kamchatka", "Irkutsk", "Eastern Russia"]

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
        
    #Select a Random Action
    myaction = random.choice(actions)
    
    # Claim the first unowned territory in territoryPriority array.
    if state.turn_type == 'PreAssign':
        #Cycle through all of the territories, by order of importance.
        for t in territoryPriority:
            for a in actions:
                # If there is an action that involves claiming this territory, claim it.
                if a.to_territory == t:
                    myaction = a
                    return myaction

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

  