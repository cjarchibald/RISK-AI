import riskengine
import riskgui
import random
import math
from aihelper import *
from risktools import *
from turbohelper import *


# This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""

    # if time_left is not None:
    # Decide how much time to spend on this decision

    if state.turn_type == 'PreAssign':
        return preAssign(state)

    # Get the possible actions in this state
    actions = getAllowedActions(state)

    #print('Heuristic AI : Player', state.players[state.current_player].name, 'considering', len(actions), 'actions, with time left: ',time_left)

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
            h = heuristic(state, successors[i] )

            current_action_value += (h * probabilities[i])

        # Store this as the best action if it is the first or better than what we have found
        if best_action_value is None or current_action_value > best_action_value:
            best_action = a
            best_action_value = current_action_value

    """
    our_t = 0
    opp_t = 0
    for t in state.board.territories:
        if is_our_territory(state, t, state.current_player):
            our_t += 1
        if is_their_territory(state, t, state.current_player):
            opp_t += 1
    #print("H:" + str(our_t) + "|O:" + str(opp_t))
    #print(best_action.description(), best_action_value )
    #print
    """

    # Return the best action
    return best_action


def preAssign(state):

    best_action = None
    best_action_value = None
    actions = getPreAssignActions(state)


    if state.players[state.current_player].free_armies >= 30:
        for a in actions:
        
            if str(a.to_territory) == "Laos":
                action_value = 7

            elif str(a.to_territory) == "Brazil":
                action_value = 6

            elif str(a.to_territory) == "Chile":
                action_value = 5
         
            elif str(a.to_territory) == "Iceland":
                action_value = 4
          
            elif str(a.to_territory)== "Alaska":
                action_value = 3
           
            elif str(a.to_territory) == "Eastern Australia":
                action_value = 2
         
            elif str(a.to_territory) == "Greenland":
                action_value = 1

            else:
                action_value = 0

            monopoly_action = checkMonopoly(state, a.to_territory)
            if monopoly_action > 0:
                action_value = monopoly_action
            
            if best_action_value is None or action_value > best_action_value:
                best_action = a
                best_action_value = action_value
                #print "Update Action: ", best_action_value         

    elif state.players[state.current_player].free_armies > 22:
        for a in actions:
            
            if str(a.to_territory)== "Alaska":
                action_value = 10
         
            elif str(a.to_territory) == "Eastern Australia":
                action_value = 9
           
            elif str(a.to_territory) == "Mexico":
                action_value = 8
        
            elif str(a.to_territory) == "Western Africa":
                action_value = 7
             
            elif str(a.to_territory) == "Western Austrialia":
                action_value = 6
             
            elif str(a.to_territory) == "Columbia":
                action_value = 5
              
            elif str(a.to_territory) == "Madagascar":
                action_value = 4
               
            elif str(a.to_territory) == "Indonesia":
                action_value = 3
          
            elif str(a.to_territory) == "South Africa":
                action_value = 2
            
            elif str(a.to_territory) == "Kamchatka":
                action_value = 1
                   
            else:
                action_value = 0

            monopoly_action = checkMonopoly(state, a.to_territory)
            if monopoly_action > 0:
                action_value = monopoly_action
          
            if best_action_value is None or action_value > best_action_value:
                best_action = a
                best_action_value = action_value
                #print "Update Action: ", best_action_value
                
        #print "Best Action: ", best_action.to_territory
    else:
        bestPer = 0.0
        for a in actions:
            terrPer = checkPercentage(state, a.to_territory)
            monopoly_action = checkMonopoly(state, a.to_territory)
            if monopoly_action > 0:
                terrPer = monopoly_action

            if bestPer == 0.0 or terrPer > bestPer:
                best_action = a
                bestPer= terrPer  

        #print "Best Action: ", best_action.to_territory
        #print "Best Action Value: ", bestPer

    return best_action


def heuristic(original_state, state):
    """Returns a number telling how good this state is"""

    #Go through all territory evaluations and determine state based on their attractiveness
    h = 0

    if original_state.turn_type == 'PreAssign':
        h = pre_assign_heuristic(state, original_state.current_player)

    if original_state.turn_type == 'PrePlace':
        h = pre_place_heuristic(state, original_state.current_player)

    if original_state.turn_type == 'Place':
        h = pre_place_heuristic(state, original_state.current_player)

    # Commenting this section out speeds up games much quicker
    # Having this in the code drastically improved win rates
    if state.turn_type == 'TurnInCards':
        h = pre_place_heuristic(state, original_state.current_player)

    if original_state.turn_type == 'Attack':
        h = attack_heuristic(state, original_state.current_player)

    if original_state.turn_type == 'Occupy':
        h = pre_place_heuristic(state, original_state.current_player)

    if original_state.turn_type == 'Fortify':
        h = pre_place_heuristic(state, original_state.current_player)

    return h


def attack_heuristic(state, opid):

    h = 0

    # h = pre_place_heuristic(state, opid)

    for t in state.board.territories:

        if is_our_territory(state, t, opid):

            h += 1 * state.armies[t.id]

        else:
            h -= 2 * state.armies[t.id]

    # Determine any continent bonuses we deserve
    for c in state.board.continents:
        if is_our_continent(state, state.board.continents[c], opid):
            h += 100

    # Determine any continent bonuses the opponent is receiving
    for c in state.board.continents:
        if is_their_continent(state, state.board.continents[c], opid):
            h -= 50

    return h


def pre_place_heuristic(state, opid):
    """
    Prioritize armies on territories that border enemies.
    :param state: RiskState
    :return:
    """

    h = 0

    chokeholds = grab_chokeholds(state, opid)

    for t in state.board.territories:

        if is_our_territory(state, t, opid):

            # Look at all our neighbors.
            for n in t.neighbors:

                # If our neighbor is our enemey, then we're doing good putting armies here
                if is_our_territory(state, id_to_terr(state.board, n), opid) == False:

                    if t in chokeholds:
                        h += -2 + ((state.armies[t.id]*2.0)**(1/3.0))

                    else:
                        h += -2 + math.sqrt(state.armies[t.id])

    return h


def id_to_terr(board, id):

    for t in board.territories:
        if t.id == id:
            return t


def pre_assign_heuristic(state, opid):

    """
    Here we cut out any monopolies the enemy might get by counter picking.
    :param state: RiskState
    :return:
    """

    h = 0


    # Array of territory Ids that are not owned by a single entity.
    territories_free = []

    # Get available territories to choose
    for i in range(len(state.owners)):

        # If the territory does not have an owner add it.
        if state.owners[i] is None:
            territories_free.append(i)

    # Determine if the opponent has any continent bonuses
    # Does it really even matter at this point if we're not going more than one step ahead?

    # Determine if the opponent is one step away from any continent bonuses
    opponent_step_away = False
    for c in state.board.continents:

        continent = state.board.continents[c]

        # Array of integers indexed by RiskPlayer ids that correspond to how many territories they own
        # In the current continent.  The last index in the array represents that no one owns a territory.
        owners = [0]*(len(state.board.players)+1)

        # go through and figure out who owns what inside the continent
        for t_index in range(len(state.board.territories)):

            t = state.board.territories[t_index]

            # If this territory is appart of the continent we're currently looking at..
            if t.id in continent.territories:

                # If its noe add to the None owner represented by the last index.
                if state.owners[t.id] is None:
                    owners[len(owners) - 1] += 1

                else:
                    owners[state.owners[t.id]] += 1


        # Opponent is one step away if there is one unowned territory and the rest are owned by a single player
        if owners[len(owners) - 1] == 1:

            for i in range(len(owners)-1):

                if owners[i] == len(continent.territories)-1 and i != opid:
                    opponent_step_away = True

    if opponent_step_away:
        h -= 200


    # Determine if we have any continent bonuses
    for c in state.board.continents:
        if is_our_continent(state, state.board.continents[c], opid):
            h += 50

    # Bonus given to less, larger clusters
    regions = grab_regions(state, opid)
    h += 50 - (len(regions)*20)

    return h


def territories_are_neighbors(board, t_id1, t_id2):

    """
    Determines whether or not two territories are neighbors to each other
    :param board: RiskBoard
    :param t_id1: int
    :param t_id2: int
    :return: boolean
    """

    for t in board.territories:
        if t.id == t_id1:
            for n in t.neighbors:
                if n == t_id2:
                    return True

    return False


def is_our_continent(state, continent, opid):

    """
    :param state: RiskState
    :param continent: RiskContinent
    :return: boolean
    """

    for t in continent.territories:
        if is_our_territory(state, state.board.territories[t], opid) is False:
            return False

    return True


def is_their_continent(state, continent, opid):

    for t in continent.territories:
        if is_their_territory(state, state.board.territories[t], opid) is False:
            return False

    return True


def evalContinent(state):
    return 0


def eval_territory(state, territory):
    """
    This ranks territories on how important they are to the AI
    If this is our territory we want to protect it.
    If this is an enemies territory we want to claim it.
    :type state: RiskState
    :type territory: int
    """


    # This is the variable containing how much appeal this territory has to our agent.
    t_appeal = 0

    # figure out what continent the territory is in..
    continent = None

    # Find the continent the terriroty is contained in
    for cont in state.board.continents:

        if territory.id in state.board.continents[cont].territories:
            continent = state.board.continents[cont]

    # If this belongs to a continent that we own it's more important to us.
    if is_our_continent(state, continent):
        t_appeal += 50

    # If this territory is completely surrounded by it's friendly territories don't bother with it..

    # Grab all our neighbors
    neighbors = territory.neighbors

    neighbors_are_same_owner = True

    for n in neighbors:
        if state.owners[territory.id] != state.owners[n]:
            neighbors_are_same_owner = False

    if neighbors_are_same_owner:
        t_appeal = 0

    # Go through each neighbor and look at their armies.

    for neighbor in neighbors:

        if state.board.territories != None:

            # if the neighbor is ours the appeal is greater the more armies we have surrounding this territory
            if is_our_territory(state, state.board.territories[neighbor]):
                t_appeal += state.armies[neighbor]
            else:
                t_appeal -= state.armies[neighbor]


    return t_appeal


def is_our_territory(state, territory, opid):

    """
    Determines whether or not the territory passed in belongs to our AI given the current state of things.
    Assumes that state is in opponents phase
    :param state: RiskState
    :param territory: RiskTerritory
    :return: boolean
    """

    if state.owners[territory.id] == opid:
        return True

    return False


def is_their_territory(state, territory, opid):

    if state.owners[territory.id] != opid and state.owners[territory.id] is not None:
        return True

    return False


def grab_chokeholds(state, opid):

    """
    A choke hold is defined as a friendly territory on the outskirts of a region that touches an enemy territory that
    no other territory of that region touches.
    These are essential for reinforcement to prevent region from being broken into.
    :param state: RiskState
    :return: RiskTerritory[]
    """

    chokeholds = []

    # after writing grab_regions and grab_region I thought of a simpler better way...

    # Go through all territories on board
    for territory in state.board.territories:

        # If this terriroty is out territory.
        if is_our_territory(state, territory, opid) == False:

            our_territories_it_touches = []

            for neighbor in territory.neighbors:

                if is_our_territory(state, state.board.territories[neighbor], opid):

                    our_territories_it_touches.append(state.board.territories[neighbor])

            if len(our_territories_it_touches) == 1:
                chokeholds += our_territories_it_touches

    return list(set(chokeholds))


def grab_regions(state, opid):

    """
    Goes through and finds clusters of territories.
    :param state: RiskState
    :return: RiskTerritory[][]
    """

    # An Array of RiskTerritory[] to represent different regions
    regions = []

    # Go through all territories on board and build regions from them
    for territory in state.board.territories:

        # If this terriroty is ours lets try creating a region out of it
        if is_our_territory(state, territory, opid):

            contained_in_another_region = False

            # Go through all our regions and make sure it doesn't already exist in there.
            for region in regions:

                for t in region:

                    if t.id == territory.id:
                        contained_in_another_region = True

            # Territory is not already in another region, we can create a new region!
            if contained_in_another_region is False:

                regions.append(grab_region(state, territory, None, opid))


    return regions


def grab_region(state, territory, already_found, opid):

    """
    Recursive function that grabs all territories of ours that are touching another one of our territories in a link.
    Example if we have 3 territories bordering each other, you pass this one of those territories and it returns an
    array of all 3 of those territories.
    :param state: RiskState
    :param territory: RiskTerritory
    :param already_found: RiskTerritory[]
    :return: RiskTerritory[]
    """

    region = []

    if already_found is None or territory not in already_found:
        region.append(territory)

    if already_found is not None:
        region += already_found


    for neighbor in territory.neighbors:

        if already_found is not None and state.board.territories[neighbor] in already_found:
            continue

        if is_our_territory(state, state.board.territories[neighbor], opid):

            # Add all friendly neighbors
            region += grab_region(state, state.board.territories[neighbor], region, opid)

    # Return a set to avoid duplicates.
    return list(set(region))


def checkPercentage(state, territory):
    iOwn = 0
    tOwn = 0
    uOwn = 0
    total = 0
    iPer = 0.0
    tPer = 0.0
    uPer = 0.0
    totalPer = 0.0

    for c in state.board.continents:
        for t in state.board.continents[c].territories:
            if territory == state.board.territories[t].name:
                continent = c
 
    for t in state.board.continents[continent].territories:
        if is_our_territory(state, state.board.territories[t],state.current_player):
            iOwn += 1
        elif is_their_territory(state, state.board.territories[t], state.current_player):
            tOwn += 1 
        else:
            uOwn += 1

    num = iOwn + tOwn + uOwn
    if iOwn == num:
        return 0
    subtotal = iOwn + (num - tOwn) + (num - uOwn)  
    total = subtotal * 10
    totalPer = total / num
    return totalPer


def checkMonopoly(state, territory): 

    Owned = 0
    Appeal = 0
    notOwned = 0
    theyOwn = 0
    continent = None

    for c in state.board.continents:
        
        for t in state.board.continents[c].territories:
            if territory == state.board.territories[t].name:
                continent = c
    
    for t in state.board.continents[continent].territories:
        if is_our_territory(state,state.board.territories[t], state.current_player):
            Owned += 1
         
        elif is_their_territory(state, state.board.territories[t],state.current_player):
            theyOwn += 1
       
        else:
            notOwned += 1
        
    if len(state.board.continents[continent].territories) == (Owned + 1) or len(state.board.continents[continent].territories) == (theyOwn + 1) or len(state.board.continents[continent].territories) == (theyOwn + Owned + 1):
        Appeal += 50 
    if len(state.board.continents[continent].territories) == (Owned + 2):
        Appeal += 25
    if (len(state.board.continents[continent].territories) == theyOwn):
        Appeal += 200    

    return Appeal



# Stuff below this is just to interface with Risk.pyw GUI version
# DO NOT MODIFY

def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    print('AI Wrapper created state. . . ')
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