import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *
from creationtools import *
import math
import json
from Queue import PriorityQueue

my_id = None

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    global my_id
    #if time_left is not None:
        #Decide how much time to spend on this decision
        
    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    my_id = state.current_player
     
     
    # Handle Each turn type separately
    if state.turn_type == 'PreAssign':
        return pickAssign(state, actions)
  
    if state.turn_type == 'PrePlace':
        if my_id == 0:
            return pickPlace(state,actions)
        else:
            return pickPrePlace(state,actions)
        return pickPlace(state, actions)
        
    if state.turn_type == 'Place':
        return pickPlace(state, actions)
        
    if state.turn_type == 'TurnInCards':
        return actions[0]
    
    if state.turn_type == 'Occupy':
        return pickOccupy(state,actions)
    
    if state.turn_type == 'Attack':
        return pickAttack(state, actions)    
    
    if state.turn_type == 'Fortify':
        return pickFortify(state, actions)    
    
def getNumFoes(state, t):
    global my_id
    num_f = 0
    for n in state.board.territories[t].neighbors:
        if state.owners[n] != my_id:
            num_f += state.armies[n]
    return num_f
  
    
def pickAttack(state, actions):
#Attack first territory that we don't have in continent list, as long as we have at least 4 guys on it
    conts = ['N. America', 'S. America', 'Africa', 'Europe', 'Asia', 'Australia']
    for cn in conts:
        c = state.board.continents[cn]
        for a in actions:
            if a.to_territory != None:
                if state.board.territory_to_id[a.to_territory] in c.territories:
                    diff = state.armies[state.board.territory_to_id[a.from_territory]] - state.armies[state.board.territory_to_id[a.to_territory]]
                    if state.armies[state.board.territory_to_id[a.from_territory]] > 3 or diff > 0:
                        return a
    
    return actions[-1]
    
def pickPlace(state, actions):
#Place on the first territory on a continent from list that doesn't have 
#   2 troops if non-front
#   6 troops if front
    conts = ['N. America', 'S. America', 'Africa', 'Europe', 'Asia', 'Australia']
    #conts = []
    done = False
    destination = None
    for cn in conts:
        if not done:
            terrs = []
            opps = []
            c = state.board.continents[cn]
            for t in c.territories:
                if not done:
                    if state.owners[t] == my_id:
                        terrs.append(t)
                        if isFront(state,t):
                            fr = getFront(state, t)
                            for f in fr: 
                                opps.append(f)
            if len(opps) > 0:
                #Make sure at least one neighbour has it covered
                for o in opps:
                    max_n = 0
                    max_t = None
                    for n in state.board.territories[o].neighbors:
                        if state.owners[n] == my_id:
                            if state.armies[n] > max_n:
                                max_n = state.armies[n]
                                max_t = n
                    if max_n < getNumFoes(state,max_t) or max_n < 3:
                        destination = max_t
                        done = True
                    if done:
                        break
                        
    if destination != None:
        for a in actions:
            if state.board.territory_to_id[a.to_territory] == destination:
                return a

    max_a = None
    max_front = 0
    for a in actions:
        t = state.board.territory_to_id[a.to_territory]
        if isFront(state,t):
            mf = getNumFoes(state,t)
            if state.armies[t] > mf + 5:
                continue
            if mf > max_front:
                max_a = a
                max_front = mf
                
    if max_a != None:
        return max_a
        
    return random.choice(actions)
    
def pickPrePlace(state, actions):
#Place on the first territory on a continent from list that doesn't have 
#   2 troops if non-front
#   6 troops if front
    conts = ['N. America', 'S. America', 'Africa', 'Europe', 'Asia', 'Australia']
    done = False
    destination = None
    for cn in conts:
        if not done:
            c = state.board.continents[cn]
            for t in c.territories:
                if not done:
                    if state.owners[t] == my_id:
                        target = 2
                        if isFront(state, t):
                            target = max(5,getNumFoes(state,t))
                        if state.armies[t] < target:
                            destination = t
                            done = True
                            
    if destination != None:
        for a in actions:
            if state.board.territory_to_id[a.to_territory] == destination:
                return a

    max_a = None
    max_front = 0
    for a in actions:
        t = state.board.territory_to_id[a.to_territory]
        if isFront(state,t):
            mf = getNumFoes(state,t)
            if mf > max_front:
                max_a = a
                max_front = mf
                
    if max_a != None:
        return max_a
        
    return actions[0]

def getFront(state, t):
    front = []
    pid = state.owners[t]
    
    for n in state.board.territories[t].neighbors:
        if state.owners[n] != pid:
            if n not in front:
                front.append(n)

    return front
    
def isFront(state, t):
    pid = state.owners[t]

    for n in state.board.territories[t].neighbors:
        if state.owners[n] != pid:
            return True

    return False
    
    
    
def pickFortify(state, actions):
    max_a = None
    max_front = 0
    for a in actions:
        if a.to_territory != None:
            t = state.board.territory_to_id[a.to_territory]
        
            if isFront(state,t):
                mf = getNumFoes(state,t)
                if mf > max_front:
                    max_a = a
                    max_front = mf
                
    if max_a != None:
        return max_a
        
    return random.choice(actions)
    
def pickOccupy(state, actions):
    max_troops = 0
    best_a = actions[0]
    to_front = isFront(state, state.board.territory_to_id[best_a.to_territory])
    from_front = isFront(state, state.board.territory_to_id[best_a.from_territory])
    total_troops = state.armies[state.board.territory_to_id[best_a.from_territory]]
    target_troops = int(total_troops / 2)
    if not(to_front and from_front):
        if to_front:
            target = total_troops
        if from_front:
            target = 0
    best_diff = total_troops + 100
    for a in actions:
        cur_diff = abs(a.troops - target_troops)

        if cur_diff < best_diff:
            best_diff = cur_diff
            best_a = a
    return best_a
    
    
def pickAssign(state, actions):
    terrs = ['Kamchatka', 'Colombia', 'Iceland', 'Alaska', 'Mexico', 'Greenland', 'Quebec', 'Eastern U.S.', 'Western U.S.', 'Ontario', 'British Columbia', 'NorthwestTerritories', 'Middle East', 'Western Africa', 'Brazil', 'Chile', 'Peru', 'Indonesia', 'Zaire', 'Ethiopia', 'Egypt', 'Madagascar', 'Western Europe', 'Great Britain', 'Sweden', 'Central Europe', 'Southern Europe', 'Ukraine', 'Pakistan', 'Russia', 'India', 'China', 'Manchuria', 'Japan', 'Siberia', 'Eastern Russia', 'Irkutsk', 'New Guinea', 'Western Australia', 'Eastern Australia', 'Laos']
    
    target = None
    
    for t in terrs:
        if state.owners[state.board.territory_to_id[t]] is None:
            target = state.board.territory_to_id[t]
            break
    
    if target != None:
        for a in actions:
            if state.board.territory_to_id[a.to_territory] == target:
                return a
    
    return actions[0]
        
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

  