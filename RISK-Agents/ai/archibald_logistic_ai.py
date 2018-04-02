import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *
from pa2_learn_d_tree import *
from creationtools import *
import json

myDTree = None
my_id = None

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    global my_id
    #if time_left is not None:
        #Decide how much time to spend on this decision
    
    global myDTree

    #print 'Selecting actions from a ', state.turn_type, ' state'
    
    if myDTree is None:
        print 'Loading DTree'
        myDTree = loadDTree('pa2_trees\Dataset_216918_attacker_ai_P1_attacker_ai_P2_20141107-085947_10.dtree')
        print 'Done.'
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    my_id = state.current_player
    
    #To keep track of the best action we find
    best_action = None
    best_action_value = None
    
    #With some small probability, select random action
    r = random.random()
    if r < 0.01:
        return random.choice(actions)
    
    if state.turn_type == 'PreAssign':
        return pickAssign(state, actions)
    
    if state.turn_type == 'TurnInCards':
        return actions[0]

        
    #Count number of troops
    my_troops = 0
    opp_troops = 0
    for t in range(len(state.owners)):
        if state.owners == state.current_player:
            my_troops += state.armies[t]
        else:
            opp_troops += state.armies[t]
    
    if my_troops > opp_troops*3:
        return finalAttack(state, actions)
        
    #Evaluate each action
    possible_actions = []
        
    if state.turn_type == 'Place' or state.turn_type == 'Fortify' or state.turn_type == 'PrePlace':
        for a in actions:
            #Simulate the action, get all possible successors
            successors, probabilities = simulateAction(state, a)
              
            #Compute the expected heuristic value of the successors
            current_action_value = 0.0
        
            for i in range(len(successors)):
                #Each successor contributes its heuristic value * its probability to this action's value
                current_action_value += (p_heuristic(successors[i],a) * probabilities[i])
        
            #Store this as the best action if it is the first or better than what we have found
            if best_action_value is None or current_action_value > best_action_value:
                possible_actions = [a]
                best_action_value = current_action_value
            elif current_action_value == best_action_value:
                possible_actions.append(a)
    
    if state.turn_type == 'Attack':
        for a in actions:
            #Simulate the action, get all possible successors
            successors, probabilities = simulateAction(state, a)
              
            #Compute the expected heuristic value of the successors
            current_action_value = 0.0
        
            for i in range(len(successors)):
                #Each successor contributes its heuristic value * its probability to this action's value
                current_action_value += (dfs_heuristic(successors[i]) * probabilities[i])
        
            #Store this as the best action if it is the first or better than what we have found
            if best_action_value is None or current_action_value > best_action_value:
                possible_actions = [a]
                best_action_value = current_action_value
            elif current_action_value == best_action_value:
                possible_actions.append(a)
        
    #Return the best action
    if len(possible_actions) > 0:
        return random.choice(possible_actions)

    return random.choice(actions)
    
def finalAttack(state, actions):
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
    
def pickAssign(state, actions):
    
    #Set up the data instance to pass into the decision tree
    
    #Are we the first player?
    first_player = 0
    if state.current_player == 0:
        first_player = 1
        
    owners = state.owners[:]
    for t in range(len(owners)):
        if owners[t] == state.current_player:
            owners[t] = 1
        elif owners[t] is not None:
            owners[t] = 0
            
    owners.insert(0,first_player)
    
    best_v = -1
    best_a = None
    
    for a in actions:
        instance = owners[:]
        instance[state.board.territory_to_id[a.to_territory]+1] = 1
        av = evaluateAssignAction(instance, a)
        if av > best_v:
            best_v = av
            best_a = a
    
    return best_a
    
def evaluateAssignAction(instance, action):
    #Randomly complete the rest of the instance
    snones = []
    
    for t in range(len(instance)):
        if t is None:
            snones.append(t)
    
    num_samples = 100
    action_value = 0
    
    for s in range(num_samples):
        new_owner = 0
        nones = snones[:]
    
        while len(nones) > 0:
            nt = random.choice(nones)
            nones.remove(nt)
            instance[nt] = new_owner
            if new_owner == 0:
                new_owner = 1
            else:
                new_owner = 0
    
        #Randomly filled out instance, evaluate
        action_value  += myDTree.get_prob_of_win(instance)
    
    return float(action_value) / float(num_samples)
    
def dfs_heuristic(state):
    """Get the maximum heuristic value for player from current state, assuming expected battle outcomes"""
    max_value = heuristic(state)
    if max(state.owners) == min(state.owners):
        return 1.0   
    
    #See about all the territories the player could attack
    for i in range(len(state.owners)):
        if state.owners[i] == my_id and state.armies[i] > 1:
            #Try all neighbors
            for j in state.board.territories[i].neighbors:
                if state.owners[i] != my_id:
                    #The player can attack
                    #Create expected post battle state and recurse
                    result = get_exp_troops_remaining(state.armies[i],state.armies[j])
                    #print 'Expected battle result is: ', result
                    copy_state = state.copy_state()
                    value = max_value
                    if result > 0:
                        #Attacker won
                        copy_state.owners[j] = my_id
                        copy_state.armies[j] = result
                        copy_state.armies[i] = 1
                        value = get_max_expansion( copy_state, my_id)
                    else:
                        #Attacker lost
                        copy_state.armies[i] = 1
                        copy_state.armies[j] = result
                        value = get_max_expansion( copy_state, my_id)
                     
                    if value > max_value:
                        max_value = value

    return max_value
    
def p_heuristic(state,action):
    #Put all free armies on this territory
    if action.to_territory is None:
        return 0
        
    to_terr = state.board.territory_to_id[action.to_territory]
    state.armies[to_terr] += state.players[state.current_player].free_armies
    
    return dfs_heuristic(state)
    
    
def heuristic(state):
    """Returns a number telling how good this state is"""
    #Use the features
    my_player = None
    for p in state.players:
        if p.id == my_id:
            my_player = p
            break
    if my_player is None:
        print 'MY PLAYER IS NONE!'
        return 0
    features = get_features(state, my_player)
    load_weights(state)
    return get_prediction(features)
    
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

  