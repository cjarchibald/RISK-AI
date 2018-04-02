####################################################################
#                                                                  #
#           CSE 4633/6633: Artificial Intelligence                 #
#           RISK Project                                           #
#           Our Agent: wow_bot                                     #
#           TEAM MEMBERS:                                          #
#           1) Naila Bushra - nb921@msstate.edu                    #
#           2) Amrita Dhakal Ghimire - ad1568@msstate.edu          #
#           3) Shelton Matthews - jsm553@msstate.edu               #
#                                                                  #
####################################################################

import random
from gui.aihelper import *
from risktools import *
from gui.turbohelper import *

# Manual listing of entry points
Entry_points = ['Indonesia', 'Colombia', 'Brazil', 'Alaska', 'Mexico', 'Greenland', 'Iceland', 'Western Europe', 'Southern Europe', 'Ukraine', 'Western Africa', 'Ethiopia', 'Egypt', 'Middle East', 'Kamchatka', 'Laos', 'Pakistan', 'Russia']

################################ Helper Functions ###############################################

# is continent_name already my continent?
def is_my_continent(state, continent_name):
     for idx in state.board.continents[continent_name].territories:
          #print state.owners[idx], '======', state.current_player
	  if state.owners[idx] != state.current_player:
          	return False
     return True

# Check for placing action, place more armies if not already my continent
def in_my_continent(to_id, state):
    if state.board.territory_to_id[to_id] in state.board.continents['Australia'].territories and is_my_continent(state, 'Australia'):
         return True
    if state.board.territory_to_id[to_id] in state.board.continents['S. America'].territories and is_my_continent(state, 'S. America'):
         return True
    if state.board.territory_to_id[to_id] in state.board.continents['N. America'].territories and is_my_continent(state, 'N. America'):
         return True
    if state.board.territory_to_id[to_id] in state.board.continents['Africa'].territories and is_my_continent(state, 'Africa'):
         return True
    if state.board.territory_to_id[to_id] in state.board.continents['Asia'].territories and is_my_continent(state, 'Asia'):
         return True
    if state.board.territory_to_id[to_id] in state.board.continents['Europe'].territories and is_my_continent(state, 'Europe'):
         return True
    return False

# takes territory id, gives back the continent name
def get_continent_name(to_id, state):
    if to_id in state.board.continents['Australia'].territories:
	return 'Australia'
    elif to_id in state.board.continents['S. America'].territories:
	return 'S. America'
    elif to_id in state.board.continents['N. America'].territories:
	return 'N. America'
    elif to_id in state.board.continents['Africa'].territories:
	return 'Africa'
    elif to_id in state.board.continents['Asia'].territories:
	return 'Asia'
    elif to_id in state.board.continents['Europe'].territories:
	return 'Europe'
    else:
        return None

# How many neighbors do I own of the territory I am trying to attack
def own_neighbors(neighbors, state):
    own_neighbor = 0
    dont_own_neighbor = 0
    for neigh in neighbors:
         if neigh is not None:
		if state.owners[neigh] == state.current_player:
			own_neighbor+=1
		else:
			dont_own_neighbor+=1
    #print '>>>>', own_neighbor
    #print '>>>>', len(neighbors)/2

    if own_neighbor >= len(neighbors)/2:
         return True
    else:
         return False

############################### Return best actions ###################################

# Returns best Preassign action
def get_preassign_action(actions, state):
     Forbidden_Territories = ['Middle East', 'Southern Europe', 'Sweden', 'China', 'Manchuria', 'Ukraine', 'Russia']
     for a in actions:
        to_terr_id = state.board.territory_to_id[a.to_territory]
        if to_terr_id in state.board.continents['Australia'].territories:
             #print 'Placing in australia'
             return a 
     for a in actions:
        to_terr_id = state.board.territory_to_id[a.to_territory]
	if to_terr_id  in state.board.continents['S. America'].territories:
	     #print 'Placing in S. America'
	     return a 
     for a in actions:
        to_terr_id = state.board.territory_to_id[a.to_territory]
        if to_terr_id in state.board.continents['N. America'].territories:
	     #print 'Placing in N. America'
	     return a 
     # Assign any territories but the Forbidden_Territories ones! Too risky otherwise
     forbidden = True
     best_action = None
     for a in actions:
        if a.to_territory not in Forbidden_Territories:
	     forbidden = False
             best_action = a
             break
     if forbidden == False:
             return best_action

     return actions[-1]
#---------------------------------------------------------------------------------------------------
# Returns best Preplace action
def get_preplace_action(actions, state):
     global Entry_points
     for a in actions:
        if a.to_territory is not None:
             to_terr_id = state.board.territory_to_id[a.to_territory]
             # Guard the entry points better
             if state.armies[to_terr_id] < 4 and a.to_territory in Entry_points:
                  #if to_terr_id in state.board.continents['Australia'].territories or to_terr_id in state.board.continents['S. America'].territories or to_terr_id in state.board.continents['N. America'].territories:
                  return a
     return None
#---------------------------------------------------------------------------------------------------
# Returns best Place action
def get_place_action(actions, state):
     #if to_terr_id in state.board.continents['Australia'].territories and not is_my_continent(state, 'Australia') and state.armies[to_terr_id] < 4:
     global Entry_points

     for a in actions:
        if a.to_territory is not None:
              to_terr_id = state.board.territory_to_id[a.to_territory]
              # Guard the entry points better
              if state.armies[to_terr_id] < 4 and a.to_territory in Entry_points:
                    #if own_neighbors(state.board.territories[to_terr_id].neighbors, state):
                    #print 'Placing in australia'
                    return a 
                    #if not in_my_continent(a.to_territory, state):
                    #return a
     return None
#---------------------------------------------------------------------------------------------------
# Returns best Fortify action
def get_fortify_action(state, actions):
    global Entry_points
    for a in actions:
        to_terr_id = state.board.territory_to_id[a.to_territory]
        # Guard the entry points better
    	if a.to_territory in Entry_points and a.to_territory is not None:
              continent_name = get_continent_name(state.board.territory_to_id[a.to_territory], state)
              #if is_my_continent(state, continent_name):
              #if state.armies[to_terr_id] > 4: # degrades performance
              #if state.armies[state.board.territory_to_id[a.to_territory]] < 4:# degrades performance
              #print 'Fortifying in entry point'
	      return a
    return None
#---------------------------------------------------------------------------------------------------
# Returns best Attack action
def get_attack_action(actions, state):
    # Heuristic
    #Evaluate each action
    '''print 'Heuristic AI : Player', state.players[state.current_player].name, 'considering', len(actions), 'actions'
    
    #To keep track of the best action we find
    best_action = None
    best_action_value = None

    for a in actions:
        #Simulate the action, get all possible successors
        successors, probabilities = simulateAction(state, a)
        #Compute the expected heuristic value of the successors
        current_action_value = 0.0
        for i in range(len(successors)):
            #Each successor contributes its heuristic value * its probability to this action's value
            current_action_value += (calc_attack_heuristic(a, successors[i], state) * probabilities[i])
        #Store this as the best action if it is the first or better than what we have found
        if best_action_value is None or current_action_value > best_action_value:
            best_action = a
            best_action_value = current_action_value
    if current_action_value == 0:
        best_action = actions[-1]
    return best_action '''
    # non-heuristic  
    best_action = None
    from_army = 0
    to_army = 1000
    max_diff = -1000
    for a in actions:
         if a.to_territory is not None and a.from_territory is not None:
                temp_from_army = state.armies[state.board.territory_to_id[a.from_territory]]
                temp_to_army = state.armies[state.board.territory_to_id[a.to_territory]]
                diff = temp_from_army - temp_to_army
                # Attack only when it is safe to do so
         	if temp_from_army > from_army and temp_to_army < to_army and diff > max_diff:
                      from_army = temp_from_army
                      to_army = temp_to_army
                      max_diff = diff
                      best_action = a

    if best_action is not None:
          return best_action           
    return actions[-1]

def calc_attack_heuristic(action, state, previous_state):
    # Don't attack if attacked once 
    if previous_state.turn_type == 'Attack':
         return 0.0
    if action.from_territory is not None:
        #print state.armies[state.board.territory_to_id[action.from_territory]]
        player_id = state.players[state.current_player].id
        if previous_state.armies[previous_state.board.territory_to_id[action.from_territory]] < 4:
	    if state.owners.count(player_id) > previous_state.owners.count(player_id):
                 return 4
 	    else:
	         return 1
        elif previous_state.armies[previous_state.board.territory_to_id[action.from_territory]] < 8:
	    if state.owners.count(player_id) > previous_state.owners.count(player_id):
	         return 4
 	    else:
                 return 2
        elif previous_state.armies[previous_state.board.territory_to_id[action.from_territory]] >= 8:
	    if state.owners.count(player_id) > previous_state.owners.count(player_id):
	         return 4
 	    else:
	         return 3
         
    return 0.0

################################### GET ACTION ######################################################

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    #if time_left is not None:
        #Decide how much time to spend on this decision
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    #To keep track of the best action we find
    best_action = None
    best_action_value = None

    #print '---->', state.owners
    #print '---->', state.armies
    #print '---->', state.current_player
    if state.turn_type == 'PreAssign':
        #print 'Choosing best action to PreAssign...'
        best_action = get_preassign_action(actions, state)
    
    if state.turn_type == 'PrePlace':
        #print 'Choosing best action to PrePlace...'
        best_action = get_preplace_action(actions, state)

    if state.turn_type == 'Place':
        #print 'Choosing best action to Place...'
        best_action = get_place_action(actions, state)

    if state.turn_type == 'Attack':
        #print 'Choosing best action for Attacking...'
        best_action = get_attack_action(actions, state)

    if state.turn_type == 'Occupy':
        #print 'Choosing best action for Occupying...'
        best_action = None # assigned randomly below

    if state.turn_type == 'Fortify':
        #print 'Choosing best action for Fortifying...'
        best_action = get_fortify_action(state, actions)

    if state.turn_type == 'TurnInCards':
        #print 'Choosing best action for TurnInCards...'
        for a in actions:
             if a.from_territory is not None and a.to_territory is not None and a.troops is not None:
                   best_action =  a
                   break
    #Select a Random Action
    if best_action == None:
	best_action = random.choice(actions)
    #print best_action.print_action()
    return best_action

######################################## GUI ################################################
       
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

  
