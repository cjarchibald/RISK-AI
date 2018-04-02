import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *
from pa2_learn_d_tree import *

ai_D_tree = None

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    global ai_D_tree

    # Load the constructed decision tree
    # By analysis, pa2_test_10.dtree performed the best, and is loaded here
    if ai_D_tree is None:
        print 'Loading new decision tree...'
        ai_D_tree = loadDTree('pa2_test_10.dtree')
        print 'Loading complete.'

    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    #To keep track of the best action we find
    best_action = None
    best_action_value = None
    
    #Evaluate each action
    # if state.turn_type == 'Attack':
    for a in actions:
               
        #Simulate the action, get all possible successors
        successors, probabilities = simulateAction(state, a)
              
        #Compute the expected heuristic value of the successors
        current_action_value = 0.0
        
        for i in range(len(successors)):
            #Each successor contributes its heuristic value * its probability to this action's value
            current_action_value += (heuristic(successors[i], state.turn_type) * probabilities[i])
        
        #Store this as the best action if it is the first or better than what we have found
        if best_action_value is None or current_action_value > best_action_value:
            best_action = a
            best_action_value = current_action_value

    # Go to function for pre-assignment
    if state.turn_type == 'PreAssign':
        best_action = chooseAssignment(state, actions)

    if state.turn_type == 'Fortify' or state.turn_type == 'PreAssign':
        possible_actions = []

        for a in actions:
            if a.to_territory is not None:
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        possible_actions.append(a)
                    
        if len(possible_actions) > 0:
            best_action = random.choice(possible_actions)

    #Return the best action
    return best_action


# Note: We are passing in the sucessesor state.
def heuristic(state, last_turn_type):
    """Returns a number telling how good this state is"""
    h_value = 0

    # Calculate the h_value for Attacking
    if last_turn_type == 'Attack':        
        if state.last_defender != None:            
            # assign higher value when we successfully attack the territory
            if state.owners[state.last_defender] == state.owners[state.last_attacker]:
                h_value += 2

            # assign higher value is the attacker's armies are greater than the defender's
            if (state.armies[state.last_attacker]-state.armies[state.last_defender]) > 0:
                h_value = 4
        if state.last_defender == None:
            h_value = 3

    # Calculate the h_value for Occupying 
    elif last_turn_type == 'Occupy':
        if state.last_defender != None:
            # If we successfully attack, assign the number of armies currently in
            # the new territory to the h_value
            if state.owners[state.last_defender] == state.owners[state.last_attacker]:
                h_value = state.armies[state.last_defender]

    # Calculate the h_value for placement
    elif last_turn_type == 'Place' or last_turn_type == 'PrePlace':
        total_army_ratio = 0.0
        most_enemy_territories = 0.0

        for each in range(len(state.owners)):
            enemy_territories = 0.0
            army_ratio = 0.0
            
            if state.owners[each] == state.current_player:
                for other in state.board.territories[each].neighbors:
                    if state.owners[other] != state.current_player:
                        army_ratio = float(state.armies[each]) / float(state.armies[other])
                        enemy_territories += 1.0
                    
            if enemy_territories > most_enemy_territories:
                most_enemy_territories = enemy_territories
                total_army_ratio += army_ratio
        
        h_value = total_army_ratio       

    return h_value

def chooseAssignment(state, actions):
    # Find if we are the first player
    first_player = 0
    if state.current_player == 0:
        first_player = 1

    owners = state.owners[:]
    for each in range(len(owners)):
        if owners[each] == state.current_player:
            owners[each] = 1
        elif owners[each] is not None:
            owners[each] = 0

    owners.insert(0, first_player)

    best_evaluation = -1
    best_action = None
    
    # Cycle through all actions, finding the one that is evaluated at the highest
    for action in actions:
        instance = owners[:]
        instance[state.board.territory_to_id[action.to_territory]+1] = 1
        new_eval = evaluateAssignment(instance, action)
        # Update evaluation & action
        if new_eval > best_evaluation:
            best_evaluation = new_eval
            best_action = action

    return best_action

def evaluateAssignment(instance, action):
    # Complete the rest of the instance at random
    none_samples = []

    for each in range(len(instance)):
        if each is None:
            none_samples.append(each)

    num_samples = 100
    action_value = 0

    for sample in range(num_samples):
        new_owner = 0
        nones = none_samples[:]

        while len(nones) > 0:
            new_choice = random.choice(nones)
            nones.remove(new_choice)
            instance[new_choice] = new_owner
            if new_owner == 0:
                new_owner = 1
            else:
                new_owner = 0

        # Evaluation of the rest of the instance
        action_value += ai_D_tree.get_prob_of_win(instance)

    return float(action_value) / float(num_samples)



#Stuff below this is just to interface with Risk.pyw GUI version
#DO NOT MODIFY
    
def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    #print 'AI Wrapper created state. . . '
    #game_state.print_state()
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

  
