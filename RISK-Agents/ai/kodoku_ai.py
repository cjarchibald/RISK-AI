# ****************************************
# Name: kodoku_ai.py
# Authors: 
#          Dillon Babb
#         Garrett Porter
#         Jordan Scruggs
# Last edited: 2016 - 11 - 30 :: 21:49:27
# ****************************************


import random
from gui.aihelper import *
from risktools import *
from gui.turbohelper import *


# This is the function implement to implement an AI.
# Then this ai will work with either the gui or the play_risk_ai script

def heuristic_operation(state, player_id):
    # Returns list of the following:
    # ratio of total_owned_countries, 
    # ratio of total_owned_countries / num_owned_bordering,
    # Border Security Ratio (BSR),
    # ratio of total_enemy_territories_bordering / num_owned_bordering,
    # ratio of self_owned_army_on_border / self_owned_army_on_interior,
    # sum of percentage owned of each continent

    # The border security ratio for a particular territory is number of enemy armies
    # divided by the owned territory's army count. I suspect that the lower the ratio,
    # the better the defense is in that area. 

    # set of territories owned
    set_owned = set()
    
    # set of bordering enemy territories
    bordering_enemy_territories = set()
    
    # number of territories on the border
    num_owned_bordering = 0

    # initializations of ratios total_owned_countries / num_owned_bordering
    # and total_enemy_territories_bordering / num_owned_bordering
    ratio_of_owned_over_owned_bordering = 0
    ratio_of_enemy_bordering_over_owned_bordering = 0

    # BSR sum
    bsr = 0
    
    # interior troop count initialization
    interior_troop_count = 0
    bordering_troop_count = 0

    # This exists to handle division by zero errors
    ratio_of_bordering_to_interior = 0

    # Filling the list_owned with the ids of the territories owned by player
    for index in range(len(state.owners)):
        if state.owners[index] == player_id:
            set_owned.add(index)
    
    # Initial value of percentage owned of continents
    percentage_of_continents = 0
    
    # The following loop finds and adds up the percentage owned of each continent
    for key, item in state.board.continents.items():
       percentage_of_continents += len(set_owned.intersection(item.territories)) / len(item.territories)
    
    # Iterates through each element in the set_owned set
    for ter_id in set_owned:
        # Checks to see if all the neighbors that this particular territory are those owned
        # if not, then that means it is bordering country and we increment the counter
        if not set_owned.issuperset(state.board.territories[ter_id].neighbors):
            num_owned_bordering += 1
            
            # sum of enemy territory armies
            count_of_enemy_armies = 0
            
            # calculating BSR for ter_id
            for enemy_ter_id in (set(state.board.territories[ter_id].neighbors) - set_owned):
                # adding up armies of enemy neighboring territories
                count_of_enemy_armies += state.armies[enemy_ter_id]
                
                # adding up bordering troops
                bordering_troop_count += state.armies[ter_id]
                
                # print 'Army count of', state.board.territories[enemy_ter_id].name, 'is', state.armies[enemy_ter_id]
                
                # collecting all enemy neighbors
                bordering_enemy_territories.add(enemy_ter_id)
            
            # Calculating BSR and summing it with others
            if state.armies[ter_id] != 0:
                bsr += count_of_enemy_armies / state.armies[ter_id]
        
        # This else branch is used to add up interior troop count
        else:
            interior_troop_count += state.armies[ter_id]
        
        # This runs only when there isn't a divide by zero
        if interior_troop_count != 0:
            ratio_of_bordering_to_interior = bordering_troop_count/interior_troop_count

    if num_owned_bordering != 0:
        ratio_of_owned_over_owned_bordering = len(set_owned)/num_owned_bordering
        ratio_of_enemy_bordering_over_owned_bordering = len(bordering_enemy_territories)/num_owned_bordering

    return [len(set_owned), ratio_of_owned_over_owned_bordering, bsr, ratio_of_enemy_bordering_over_owned_bordering, ratio_of_bordering_to_interior, percentage_of_continents]


def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""

    # if time_left is not None:
    # Decide how much time to spend on this decision

    # Get the possible actions in this state
    actions = getAllowedActions(state)

    #print 'Kodoku AI : Player', state.players[state.current_player].name, 'considering', len(actions), 'actions'

    # To keep track of the best action we find
    best_action = None
    best_action_value = None

    # Evaluate each action
    for a in actions:

        # Simulate the action, get all possible successors
        successors, probabilities = simulateAction(state, a)

        # Compute the expected heuristic value of the successors
        current_action_value = 0.0

        for i in range(len(successors)):

            # Each successor contributes its heuristic value * its probability to this action's value
            current_action_value += (heuristic(successors[i], state.current_player, a) * probabilities[i])

        # Store this as the best action if it is the first or better than what we have found
        if best_action_value is None or current_action_value > best_action_value:
            best_action = a
            best_action_value = current_action_value

    # Return the best action
    return best_action


def heuristic(state, player_id, action):
    """Returns a number telling how good this state is"""

    heuristics = heuristic_operation(state, player_id) # returns a list
    result = 0

    # Open multiplier file.
    if len(state.players) < 2:
        mult_file = open("kodoku_one_v_one_mult.txt", 'r')
    else:
        mult_file = open("kodoku_one_v_many_mult.txt", 'r')
    
    # Read it, and split all multipliers by spaces
    list_of_multipliers = mult_file.read().strip().split(' ')

    # Closing the file
    mult_file.close()

    if state.turn_type == 'Attack':
        ''' Attack multipliers here '''
        x = 0
        result = heuristics[0] * float(list_of_multipliers[x]) + heuristics[1] * float(list_of_multipliers[x+1]) + heuristics[2] * float(list_of_multipliers[x+2]) + heuristics[3] * float(list_of_multipliers[x+3]) + heuristics[4] * float(list_of_multipliers[x+4]) + heuristics[5] * float(list_of_multipliers[x+5])

    elif state.turn_type == 'PreAssign':
        ''' PreAssign multipliers here '''
        x = 6
        result = heuristics[0] * float(list_of_multipliers[x]) + heuristics[1] * float(list_of_multipliers[x+1]) + heuristics[2] * float(list_of_multipliers[x+2]) + heuristics[3] * float(list_of_multipliers[x+3]) + heuristics[4] * float(list_of_multipliers[x+4]) + heuristics[5] * float(list_of_multipliers[x+5])

    elif state.turn_type == 'PrePlace':
        ''' PrePlace multipliers here '''
        x = 12
        result = heuristics[0] * float(list_of_multipliers[x]) + heuristics[1] * float(list_of_multipliers[x+1]) + heuristics[2] * float(list_of_multipliers[x+2]) + heuristics[3] * float(list_of_multipliers[x+3]) + heuristics[4] * float(list_of_multipliers[x+4]) + heuristics[5] * float(list_of_multipliers[x+5])

    elif state.turn_type == 'TurnInCards':
        ''' TurnInCards multipliers here '''
        x = 18
        result = heuristics[0] * float(list_of_multipliers[x]) + heuristics[1] * float(list_of_multipliers[x+1]) + heuristics[2] * float(list_of_multipliers[x+2]) + heuristics[3] * float(list_of_multipliers[x+3]) + heuristics[4] * float(list_of_multipliers[x+4]) + heuristics[5] * float(list_of_multipliers[x+5])

    elif state.turn_type == 'Place':
        ''' Place multipliers here '''
        x = 24
        result = heuristics[0] * float(list_of_multipliers[x]) + heuristics[1] * float(list_of_multipliers[x+1]) + heuristics[2] * float(list_of_multipliers[x+2]) + heuristics[3] * float(list_of_multipliers[x+3]) + heuristics[4] * float(list_of_multipliers[x+4]) + heuristics[5] * float(list_of_multipliers[x+5])

    elif state.turn_type == 'Occupy':
        ''' Occupy multipliers here '''
        x = 30
        result = heuristics[0] * float(list_of_multipliers[x]) + heuristics[1] * float(list_of_multipliers[x+1]) + heuristics[2] * float(list_of_multipliers[x+2]) + heuristics[3] * float(list_of_multipliers[x+3]) + heuristics[4] * float(list_of_multipliers[x+4]) + heuristics[5] * float(list_of_multipliers[x+5])

    elif state.turn_type == 'Fortify':
        ''' Fortify multipliers here '''
        x = 36
        result = heuristics[0] * float(list_of_multipliers[x]) + heuristics[1] * float(list_of_multipliers[x+1]) + heuristics[2] * float(list_of_multipliers[x+2]) + heuristics[3] * float(list_of_multipliers[x+3]) + heuristics[4] * float(list_of_multipliers[x+4]) + heuristics[5] * float(list_of_multipliers[x+5])

    return result


# Stuff below this is just to interface with Risk.pyw GUI version
# DO NOT MODIFY


def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    print 'AI Wrapper created state. . . '
    game_state.print_state()
    action = getAction(game_state)
    return translateAction(game_state, action)


def Assignment(player):
    # Need to Return the name of the chosen territory
    return aiWrapper('Assignment')


def Placement(player):
    # Need to return the name of the chosen territory
    return aiWrapper('Placement')


def Attack(player):
    # Need to return the name of the attacking territory, then the name of the defender territory
    return aiWrapper('Attack')


def Occupation(player, t1, t2):
    # Need to return the number of armies moving into new territory
    occupying = [t1.name, t2.name]
    aiWrapper('Occupation', occupying)


def Fortification(player):
    return aiWrapper('Fortification')
