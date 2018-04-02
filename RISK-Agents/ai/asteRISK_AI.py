import riskengine
import riskgui
import random
from aihelper import *
from risktools import *
from turbohelper import *


#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    #if time_left is not None:
        #Decide how much time to spend on this decision

    #Get the possible actions in this state
    actions = getAllowedActions(state)
    #print 'Heuristic AI : Player', state.players[state.current_player].name, 'considering', len(actions), 'actions'

    ''' select a random action to return in case all others fail '''
    action = random.choice(actions)

    ''' continent priority (used for preassigning) '''
    continent_priority = ["Australia", "S. America", "N. America", "Africa", "Europe", "Asia"]

    '''
        PREASSIGN
        This AI considers the priority of continents when assigning armies
        to the board using the array continent_priority and the order of
        the continents in this array
    '''
    if state.turn_type == "PreAssign":
        for continent in continent_priority: #iterate through the continent in order of priority
            for action in actions: # iterate through the allowed actions
                ''' get action's assigning to territory and the territories of continent '''
                to_territory = action.to_territory
                continent_territories = state.board.continents[continent].territories
                ''' if action's assigning to territory is in continent, return that action '''
                if state.board.territory_to_id[to_territory] in continent_territories:
                    return action

    '''
        PREPLACE
        This AI considers whether or not neighboring territories are owned
        by this AI when preplacing armies. If a neighboring owner is not
        this AI, place troops there to strengthen it.
    '''
    if state.turn_type in ["PrePlace"]:
        preplace_options = [] # array to hold decent preplace actions
        for action in actions: # iterate through the allowed actions
            ''' get action's preplacing to territory and its neighbors '''
            to_territory = action.to_territory
            territory_id = state.board.territory_to_id[to_territory]
            territory_neighbors = state.board.territories[territory_id].neighbors
            for neighbor in territory_neighbors: # iterate through the territories neighbors
                ''' if the owner of a neighbor is not this AI, it's a decent preplace '''
                if state.owners[neighbor] == state.current_player:
                    preplace_options.append(action) # add it to the preplace options
        ''' if there are decent options available, choose a random one '''
        if len(preplace_options) > 0:
            return random.choice(preplace_options)

        return random.choice(actions) # else choose a random preplace

    '''
        PLACE
        This AI considers the territories that border opponent territories
        and places troops in those that do first. It goes to each territory
        that borders an opponent territory and places one troop in a loop
        until the number of troops in each bordering territory is
        <multiplier_max> times greater than it's bordering opponent's armies
         - border: a territory that has an enemy territory as a neighbor
    '''
    place_multiplier = 2 # the starting multiplier for which the AI will try to place at a border
    multiplier_max = 6 # the max multiplier that the AI will reach when placing armies at a border
    while state.turn_type == "Place":
        for action in actions: # iterate through the allowed actions
            for territory in state.board.territories: # iterate through all territories on board
                territory_owner = state.owners[territory.id] # get the owner of territory
                territory_neighbors = territory.neighbors # get the neighbors of territory
                for neighbor in territory_neighbors: # iterate through territory's neighbors
                    to_territory = state.board.territory_to_id[action.to_territory]
                    ''' if the territory isn't the AI's and the neighboring territory is, check their armies '''
                    if territory_owner != state.current_player and territory_owner != None and neighbor == to_territory:
                        territory_armies = state.armies[to_territory] # get to_territory's armies
                        enemy_armies = state.armies[territory.id] # get enemy neighbor's armies
                        ''' if AI's armies is <place_multiplier> times or greater than the enemy's, return action '''
                        if territory_armies < place_multiplier * enemy_armies:
                            return action
        ''' if the max multiplier has been reached, this AI randomly places the remaining armies '''
        if place_multiplier > multiplier_max:
            return random.choice(actions)
            ''' else it continues placing troops along the border '''
        else:
            place_multiplier += 1.0

    '''
        ATTACK
        This AI considers the ratio of armies in the attacking territory
        and the defending armies. If the ratio is <attacking_ration> or
        greater, then the action is considered (added to attack_options).
        If no options are found, then the AI doesn't attack with risk of
        losing and losing troops.
    '''
    attacking_ratio = 1.9
    if state.turn_type == "Attack":
        attack_options = [] # array for decent attack options
        for action in actions: # iterate through the allowed actions
            if action.from_territory == None: # ignore the action to not attack for now
                break
            from_territory = action.from_territory # get the attacking from territory
            from_id = state.board.territory_to_id[from_territory] # get the id of the from territory
            to_territory = action.to_territory # get the attacking to territory
            to_id = state.board.territory_to_id[to_territory] # get the id of the to territory
            num_attack_armies = state.armies[from_id] # get the number of attacking armies
            num_defend_armies = state.armies[to_id] # get the number of defending armies
            ''' if there are more than one attacking armies and the
                attacking/defedning ratio is met, append the action
                to the attack options '''
            if num_attack_armies > 1 and num_attack_armies >= attacking_ratio * num_defend_armies:
                attack_options.append(action)
        ''' if there are decent options to choose from, choose one at random '''
        if len(attack_options) > 0:
            return random.choice(attack_options)
        ''' else don't attack '''
        return actions[-1]

    '''
        OCCUPY
        This AI doesn't really consider much when it comes to occupying.
        It returns the action that equally (or as close to equal) splits
        the armies between the from territory and the to territory.
    '''
    if state.turn_type == "Occupy":
        from_territory = actions[0].from_territory
        to_territory = actions[0].to_territory

        from_id = state.board.territory_to_id[from_territory] # get id of from territory
        from_neighbors = state.board.territories[from_id].neighbors # get neighbors of from territory
        from_enemy_neighbors = 0 # initialize the count of the from territory's enemy neighbors
        for neighbor in from_neighbors:
            if state.owners[neighbor] != state.current_player:
                from_enemy_neighbors += 1
        if from_enemy_neighbors == 0:
            return actions[(len(actions)-1)]

        to_id = state.board.territory_to_id[to_territory] # get id of from territory
        to_neighbors = state.board.territories[to_id].neighbors # get neighbors of from territory
        to_enemy_neighbors = 0 # initialize the count of the from territory's enemy neighbors
        for neighbor in to_neighbors:
            if state.owners[neighbor] != state.current_player:
                to_enemy_neighbors += 1
        if to_enemy_neighbors == 0:
            return actions[0]
        ratio = from_enemy_neighbors / (to_enemy_neighbors + from_enemy_neighbors)
        action = actions[int((len(actions)-1)*ratio)]
        return action


    '''
        FORTIFY
        This AI only considers actions that move armies from one territory
        without any neighboring enemy territories to a territory that does
    '''
    if state.turn_type == "Fortify":
        fortify_options = [] # array to hold decent fortify actions
        for action in actions: # iterate through allowed actions
            from_territory = action.from_territory # get the fortify from territory
            if from_territory != None: # don't try to do all of this if it's not
                from_id = state.board.territory_to_id[from_territory] # get id of from territory
                from_neighbors = state.board.territories[from_id].neighbors # get neighbors of from territory
                from_enemy_neighbors = 0 # initialize the count of the from territory's enemy neighbors
                to_territory = action.to_territory # get id of to territory
                to_id = state.board.territory_to_id[to_territory] # get id of to territory
                to_neighbors = state.board.territories[to_id].neighbors # get neighbors of to territory
                to_enemy_neighbors = 0 # initialize the count of the to territory's enemy neighbors
                ''' iterate through from territory's neighbors and count the number of enemy neighbors '''
                for neighbor in from_neighbors:
                    if state.owners[neighbor] != state.current_player:
                        from_enemy_neighbors += 1
                ''' iterate through to territory's neighbors and count the number of enemy neighbors '''
                for neighbor in to_neighbors:
                    if state.owners[neighbor] != state.current_player:
                        to_enemy_neighbors += 1
                ''' if from territory has zero enemy neighbors and to territory doesn't, add action to options '''
                if from_enemy_neighbors == 0 and to_enemy_neighbors != 0:
                    fortify_options.append(action)
        ''' if there are decent options to choose from, choose on at random '''
        if len(fortify_options) != 0:
            return random.choice(fortify_options)
        ''' else just return the random choice '''
        return action

    ''' if all else fails, choose the random action '''
    return action

    
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

  