import riskengine
import riskgui
import random
from aihelper import *
from turbohelper import *
from risktools import *

def compute_attack_utility(before_state, action, after_state, depth):
    score = 0.0
    
    if action.from_territory is not None and action.to_territory is not None:
        reward = 0.0
        player_id = before_state.current_player
        
        from_tid = before_state.board.territory_to_id[action.from_territory]
        to_tid = before_state.board.territory_to_id[action.to_territory]
        
        before_attacker_armies = before_state.armies[from_tid]
        before_defender_armies = before_state.armies[to_tid]
        
        after_attacker_armies = 0
        after_defender_armies = 0
        
        if after_state.owners[from_tid] == player_id:
            after_attacker_armies = after_attacker_armies + after_state.armies[from_tid]
        else:
            after_defender_armies = after_defender_armies + after_state.armies[from_tid]
        
        if after_state.owners[to_tid] == player_id:
            after_attacker_armies = after_attacker_armies + after_state.armies[to_tid]
        else:
            after_defender_armies = after_defender_armies + after_state.armies[to_tid]
        
        armies_attacker_lost = after_attacker_armies - before_attacker_armies
        armies_defender_lost = after_defender_armies - before_defender_armies
        
        reward = float(-armies_attacker_lost + armies_defender_lost)
        
        if after_state.owners[to_tid] == player_id:
            reward += 10.0
        
        if after_state.owners[from_tid] != player_id:
            reward -= 10.0
        
        reinf_before = getReinforcementNum(before_state, player_id)
        reinf_after = getReinforcementNum(after_state, player_id)
        reward += float(reinf_after-reinf_before)
        
        if depth > 1:
            temp = float('-inf')
            if after_state.turn_type == 'Attack':
                after_state_actions = getAllowedActions(after_state)
                for after_state_action in after_state_actions:
                    action_sum = 0.0
                    after_after_states, prob = simulateAction(after_state, after_state_action)
                    for i in range(len(after_after_states)):
                        action_sum = action_sum + compute_attack_utility(after_state, after_state_action, after_after_states[i], depth-1)*prob[i]
                    temp = max(temp, action_sum)
            score = max(score, temp)
        
        score = score + reward
    else:
        score = 0.0
    
    return score

def choose_attack_action(state):
    actions = getAllowedActions(state)
    
    max_utility_action = None
    max_utility = float('-inf')
    
    for action in actions:
        after_states, prob = simulateAction(state, action)
        for i in range(len(after_states)):
            utility = compute_attack_utility(state, action, after_states[i], 2)*prob[i]
            
            if max_utility < utility:
                max_utility = utility
                max_utility_action = action
    
    return max_utility_action

def choose_place_action(state):
    player_id = state.current_player
    actions = getAllowedActions(state)
    min_ratio_action = None
    min_ratio = float('inf')
    
    for action in actions:
        to_tid = state.board.territory_to_id[action.to_territory]
        ratio = 0.0
        count = 0
        for nbr_tid in state.board.territories[to_tid].neighbors:
            if state.owners[nbr_tid] != player_id:
                count = count + 1
                ratio = ratio + float(state.armies[nbr_tid])
        if count > 0:
            ratio = ratio / float(state.armies[to_tid])
        if ratio > 0.4:
            if min_ratio > ratio:
                min_ratio = ratio
                min_ratio_action = action
    
    if min_ratio_action is not None:
        return min_ratio_action
    else:
        return random.choice(actions)

def choose_fortify_action(state):
    player_id = state.current_player
    actions = getAllowedActions(state)
    possible_actions = []
    do_nothing_action = None
    max_ratio_change = 0.0
    for action in actions:
        if action.to_territory is not None and action.from_territory is not None:
            to_tid = state.board.territory_to_id[action.to_territory]
            from_tid = state.board.territory_to_id[action.from_territory]
            
            to_sum = 0.0
            to_ratio_before = 0.0
            to_ratio_after = 0.0
            
            from_sum = 0.0
            from_ratio_before = 0.0
            from_ratio_after = 0.0
            
            count = 0
            for nbr_tid in state.board.territories[to_tid].neighbors:
                if state.owners[nbr_tid] != player_id:
                    count = count + 1
                    to_sum = to_sum + float(state.armies[nbr_tid])
            if count > 0:
                to_ratio_before = to_sum / float(state.armies[to_tid])
                to_ratio_after = to_sum / float(state.armies[to_tid]+action.troops)
            
            count = 0
            for nbr_tid in state.board.territories[from_tid].neighbors:
                if state.owners[nbr_tid] != player_id:
                    count = count + 1
                    from_sum = from_sum + float(state.armies[nbr_tid])
            if count > 0:
                from_ratio_before = from_sum / float(state.armies[from_tid])
                from_ratio_after = from_sum / float(state.armies[from_tid]-action.troops)
            
            if to_ratio_before > 0.4 and from_ratio_before < 0.4 and from_ratio_after < 0.4:
                #possible_actions.append(action)
                ratio_change = abs(to_ratio_before - to_ratio_after)
                if max_ratio_change <= ratio_change:
                    if max_ratio_change == ratio_change:
                        possible_actions.append(action)
                    else:
                        possible_actions = []
                        max_ratio_change = ratio_change
                        possible_actions.append(action)
        else:
            do_nothing_action = action
    
    if possible_actions:
        return random.choice(possible_actions)
    else:
        return do_nothing_action

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    myaction = None
    
    if state.turn_type == 'PreAssign':
        free_territories_id = [];
        for i in range(len(state.owners)):
            if state.owners[i] is None:
                free_territories_id.append(i);
        
        if free_territories_id:
            free_continents = {}
            for c in state.board.continents.values():
                if set(free_territories_id) & set(c.territories):
                    free_continents[c.name] = 0.0
            
            for c in free_continents.keys():
                nall_t_in_c = len(state.board.continents[c].territories)
                nmy_t_in_c = 0
                nopp_t_in_c = 0
                nfree_t_in_c = 0
                for ti in range(len(state.board.continents[c].territories)):
                    if state.owners[state.board.continents[c].territories[ti]] == None:
                        nfree_t_in_c = nfree_t_in_c+1
                    elif state.owners[state.board.continents[c].territories[ti]] == state.current_player:
                        nmy_t_in_c = nmy_t_in_c+1
                    else:
                        nopp_t_in_c = nopp_t_in_c+1
                free_continents[c] = (1.0+float(nmy_t_in_c))/float(nall_t_in_c)
            
            max_c = max(free_continents.iterkeys(), key=(lambda key: free_continents[key]))
            for ti in range(len(state.board.continents[max_c].territories)):
                if state.owners[state.board.continents[max_c].territories[ti]] == None:
                    tid = state.board.continents[max_c].territories[ti]
                    myaction = RiskAction('PreAssign', state.board.territories[tid].name, None, None)
                    break
    
    if state.turn_type == 'PrePlace':
        my_territories = {}
        for tid in range(len(state.owners)):
            if state.owners[tid] == state.current_player:
                my_territories[tid] = 0.0
                for nbr_tid in state.board.territories[tid].neighbors:
                    if state.owners[nbr_tid] != state.current_player:
                        my_territories[tid] = my_territories[tid] + float(state.armies[nbr_tid])
                my_territories[tid] = my_territories[tid] / float(state.armies[tid]);
        max_key = max(my_territories.iterkeys(), key=(lambda k:my_territories[k]))
        myaction = RiskAction('PrePlace', state.board.territories[max_key].name, None, None)
    
    if state.turn_type == 'Place':
        myaction = choose_place_action(state)
    
    if state.turn_type == 'Fortify':
        myaction = choose_fortify_action(state)

    if state.turn_type == 'Attack':
        myaction = choose_attack_action(state)

    if myaction is None:
        actions = getAllowedActions(state)
        myaction = random.choice(actions)
    
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
