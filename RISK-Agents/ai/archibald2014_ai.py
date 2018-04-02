import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *
from pa2_learn_d_tree import *
from creationtools import *
import json
from Queue import PriorityQueue

myDTree = None
my_id = None
current_missions = None

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    global my_id
    #if time_left is not None:
        #Decide how much time to spend on this decision
    
    global myDTree
    global current_missions
        
    
    #print 'Selecting actions from a ', state.turn_type, ' state'
    
    if myDTree is None:
        print 'Loading DTree'
        myDTree = loadDTree('pa2_trees\Dataset_216918_attacker_ai_P1_attacker_ai_P2_20141107-085947_10.dtree')
        print 'Done.'
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    my_id = state.current_player
    opp_id = None
    for p in state.players:
        if p.id != my_id:
            opp_id = p.id    
      
    # Handle PreAssign separately
    if state.turn_type == 'PreAssign':
        #return random.choice(actions)
        return pickAssign(state, actions)
  
    # Handle TurnInCards separately
    if state.turn_type == 'TurnInCards':
        current_missions = None
        #for a in actions:
        #    a.print_action()
        return actions[0]
    
    #Handle Occupy separately
    if state.turn_type == 'Occupy':
        a = pickOccupy(state,actions)
        return a
    
    #See if I have more troops than them and should trigger the rabid Attacking
    my_armies = 0
    their_armies = 0
    for t in range(len(state.armies)):
        if state.owners[t] == my_id:
            my_armies += state.armies[t]
        else:
            their_armies += state.armies[t] 
    
    if my_armies - their_armies > 40:
        return rabidAttackAction(state,actions)
    
    # If we don't have a current mission, we need to plan one
    # This is for PrePlace, Place and Attack actions
    if current_missions is None:
        missions = []
    
        #Create a CARD mission
        m = Mission(None, state.players[my_id].free_armies, 'CARD', my_id, opp_id)
        missions.append(m)
    
        my_owned = get_completed_continents( state, my_id)
        if state.players[my_id].free_armies > 0:
            # See if we have a complete continent, if so, create mission to fortify it
            for c in my_owned:
                m = Mission(c, state.players[my_id].free_armies, 'DEFEND',my_id,opp_id)
                missions.append(m)
    
        # See if the opponent has any complete continent, if so, create mission to stop them
        opp_owned = get_completed_continents( state, opp_id)
        for c in opp_owned:
            m = Mission(c, state.players[my_id].free_armies, 'STOP',my_id,opp_id)
            missions.append(m)
        
        # For other continents, create mission to try and take it
        for c in state.board.continents:
            if c not in opp_owned and c not in my_owned:
                m = Mission(c, state.players[my_id].free_armies, 'TAKE',my_id,opp_id)
                missions.append(m)
    
        # Process each mission.  Determine number of troops required to achieve mission at some percentage
        select_current_missions( state, missions )
    
    # If we already have one, we can just do what it says
    return execute_mission( state, actions ) 

def select_current_missions( state, missions):
    """Decide on a set of missions and a priority to achieve them"""
    global current_missions
    
    current_missions = []
    
    #Process each mission to determine best path to success
    for m in missions:
        m.process_mission( state )
                
    #Now add any STOP missions
    cost_sum = 0
    for m in missions:
        if m.type == 'STOP':
            current_missions.append(m)  
            cost_sum += m.cost
    
    remaining_attackers = max(0, state.players[state.current_player].free_armies - cost_sum)
            
    #Now choose the TAKE missions we can and add them
    pq = PriorityQueue()
    for m in missions:
        if m.type == 'TAKE' and len(m.start_territories) > 0:
            pq.put([m.cost, m])
            
    done = False
    take_cost = 0
    if pq.empty():
        done = True
    else:
        fc,fm = pq.get()
        current_missions.append(fm)
        take_cost = fc
    
    while not done and not pq.empty():
        curc, curm = pq.get()
        if take_cost + curc > remaining_attackers:
            done = True
        else:
            current_missions.append(curm)
            take_cost += curc
    
    #Add in the card mission
    for m in missions:
        if m.type == 'CARD':
            current_missions.append(m)
      
    #Add in all of the DEFEND missions
    for m in missions:
        if m.type == 'DEFEND':
            current_missions.append(m)
      
    #Decide which missions to try to achieve this turn
    #print 'NEW MISSIONS for player ', my_id
    #print 'OWNERS: '
    #for i in range(len(state.owners)):
    #    print ' ', i, ' => ', state.owners[i], ' (', state.board.territories[i].name, ' ) :', state.armies[i], ' troops'
    #for m in current_missions:
     #   m.print_mission()
    #print 'ALL MISSIONS:'
    #for m in missions:
    #    m.print_mission() 
    
    #pause()
    
#This function will play as the attacking agent. 
def rabidAttackAction(state, actions):        
    #Select a Random Action
    myaction = random.choice(actions)
    
    if state.turn_type == 'Attack':
        myaction = actions[0]
    
    if state.turn_type == 'Place' or state.turn_type == 'Fortify' or state.turn_type == 'PrePlace':
        possible_actions = []

        for a in actions:
            if a.to_territory is not None:
                if isFront(state, state.board.territory_to_id[a.to_territory]):
                    possible_actions.append(a)
                    
        if len(possible_actions) > 0:
            myaction = random.choice(possible_actions)
                    
    return myaction
    
    
def isFront(state, t):
    pid = state.owners[t]
    for n in state.board.territories[t].neighbors:
        if state.owners[n] != pid:
            return True
    return False
    
def execute_mission( state, actions):
    global current_missions

    if state.turn_type == 'Fortify':
        #Move troops to a starting location that is also a front
        targets = []
        for m in current_missions:
            for t in m.start_territories:
                if t not in targets and isFront(state, t):
                    targets.append(t)
                    
        #Find the action with this target_t
        for a in actions:
            if a.to_territory is not None:
                if not isFront(state, state.board.territory_to_id[a.from_territory]) and state.board.territory_to_id[a.to_territory] in targets:
                    return a
                        
        for a in actions:
            if a.to_territory is not None:
                if not isFront(state, state.board.territory_to_id[a.from_territory]) and isFront(state, state.board.territory_to_id[a.to_territory]):
                    return a
                    
        return actions[-1]
    
    if state.turn_type == 'PrePlace' or state.turn_type == 'Place':
        #print 'Choosing preplace or place action'
        target = None
        
        for m in current_missions:
            for i in range(len(m.start_territories)):
#                if isFront(state, m.start_territories[i]) and state.armies[m.start_territories[i]] < m.place_armies[i]:                
                if state.armies[m.start_territories[i]] < m.place_armies[i]:
                    target = m.start_territories[i]
                    break
                if target is not None:
                    break
            if target is not None:
                break
                
        if state.turn_type == 'PrePlace':
            current_missions = None

        if target is None:
            current_missions = None
            #print 'Choosing Random PrePlace or Place'
            front_actions = []
            for a in actions:
                if a.to_territory is not None and isFront(state, state.board.territory_to_id[a.to_territory]):
                    front_actions.append(a)
            if len(front_actions) > 0:
                return random.choice(front_actions)
            else:
                return random.choice(actions)
        
        #Find the action with this target_t
        for a in actions:
            if a.to_territory is not None:
                if state.board.territory_to_id[a.to_territory] == target:
                    return a
    
    if state.turn_type == 'Attack':
        #Got through and find all the path points that are not conquered
        #Add these to the list of targets
        #Choose the attack on those that will give us the most troops left 
        #Over.  If none of these are positive, then end the turn
        targets = []
        stop_targets = []
        
        for m in current_missions:
            if m.type == 'DEFEND':
                continue
            for i in range(len(m.start_territories)):
                for j in range(len(m.paths[i])):
                    if state.owners[m.paths[i][j]] != my_id:
                        targets.append(m.paths[i][j])
                        if m.type == 'STOP':
                            stop_targets.append(m.paths[i][j])
                            
        #Now all of the potential targets are arranged
        most_troops_left = 0
        best_a = None
        noneA = None
                   
        for a in actions:
            if a.to_territory is None:
                noneA = a
            elif state.board.territory_to_id[a.to_territory] in targets:
                aid = state.board.territory_to_id[a.from_territory]
                did = state.board.territory_to_id[a.to_territory]
                #Get expected troops remaining from this battle
                aa = state.armies[aid]
                dd = state.armies[did]    
                exp_rem = get_exp_troops_remaining(aa,dd)
                if aid in stop_targets:
                    exp_rem = 1000
                if exp_rem > most_troops_left:
                    most_troops_left = exp_rem
                    best_a = a
                    
        if best_a is not None:
            return best_a
                    
        #Return the stop attack action
        if noneA is not None:
            return noneA
            
    #Somehow we didn't find anything that matched, so pick random action from the current set
    return random.choice(actions)
    
def pickOccupy(state, actions):
    max_troops = 0
    best_a = actions[0]
    for a in actions:
        if a.troops > max_troops:
            max_troops = a.troops
            best_a = a

    return best_a
    
    
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
        if instance[t] is None:
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

  