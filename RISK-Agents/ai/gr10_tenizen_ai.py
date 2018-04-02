import riskengine
import riskgui
import random
from turbohelper import *
from risktools import *

def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""

    #Get the possible actions in this state
    actions = getAllowedActions(state)

    myaction = random.choice(actions)

    if state.turn_type == 'Fortify':
        MaxRatio = 0
        for a in actions:
            if a.to_territory != None and a.from_territory != None:
                if myTPressure(state, state.board.territory_to_id[a.to_territory]) > state.armies[state.board.territory_to_id[a.to_territory]]: #Check that our position being fortified is in attacker range
                    if myTStrongestFront(state, state.board.territory_to_id[a.from_territory]) == state.board.territory_to_id[a.from_territory] or not myTIsFront(state, state.board.territory_to_id[a.from_territory]) : #Ensure the fortifier isn't in attacker range
                        ratio = myTPressure(state, [state.board.territory_to_id[a.to_territory]]) * 1.0 / state.armies[state.board.territory_to_id[a.from_territory]]
                        if ratio > MaxRatio: #Select the fortifier with the most troops to send
                            MaxRatio = ratio
                            myaction = a

    elif state.turn_type == 'Attack':
        possible_actions = []
        for a in actions:
            if a.to_territory != None and a.from_territory != None:
                if myTStrongestFront(state, state.board.territory_to_id[a.from_territory]) == state.board.territory_to_id[a.to_territory]:
                    possible_actions.append(a)
        if len(possible_actions) > 0:
            myaction = random.choice(possible_actions)

    elif state.turn_type == 'PrePlace':
        possible_actions = []
        for a in actions:
            if a.to_territory is not None:
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        possible_actions.append(a)
        if len(possible_actions) > 0:
            myaction = random.choice(possible_actions)

    elif state.turn_type == 'Place':
        possible_actions = []
        for a in actions:
            if a.to_territory is not None:
                if myTPressure(state, state.board.territory_to_id[a.to_territory]) > state.armies[state.board.territory_to_id[a.to_territory]]:
                    possible_actions.append(a)        
        if len(possible_actions) > 0:
            myaction = random.choice(possible_actions)
            
    return myaction

def myTIsFront(state, terr, player=None):
    if player == None:
        player = state.current_player
    if state.owners[terr] != player:
        return False
    else:
        for x in state.board.territories[terr].neighbors:
            if state.owners[x] != player:
                return True
    return True

def myTPressure(state, terr, player=None):
    if player == None:
        player = state.current_player
    return sum([state.armies[i] for i in state.board.territories[terr].neighbors if state.owners[i] != player])

def myTWeakestFront(state, t, player=None):
    if player is None:
        state = state.current_player
    if t is None:
        return None
    arms = 1000
    terr = None
    for i in state.board.territories[t].neighbors:
        if state.owners[i] != player:
            if state.armies[i] < arms:
                arms = state.armies[i]
                terr = i
    return terr

def myTStrongestFront(state, t, player=None):
    if player is None:
        player = state.current_player
    arms = -1
    terrout = None
    for i in state.board.territories[t].neighbors:
        if state.owners[i] != player:
            if state.armies[i] > arms:
                arms = state.armies[i]
                terrout = i
    return terrout

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

  
