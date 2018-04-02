from __future__ import print_function
from risktools import *


def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    # Continent priority scores
    continent_scores = {"N. America": 0, "S. America": 3, "Africa": 0, "Europe": 0, "Asia": 0, "Australia": 3}
    # Territories bordering other continents
    border_territories = (0, 2, 8, 9, 10, 16, 17, 19, 21, 24, 25, 26, 27, 28, 30, 37, 38)

    # Get the possible actions in this state
    actions = getAllowedActions(state)

    # Store actions with their score so we can prioritize
    scored_actions = []

    # Evaluate each action
    for action in actions:
        action_value = 0.0

        # In PreAssign, we prioritize continents nearly controlled by opponents, then our favorite continents, then border territories
        if state.turn_type == "PreAssign":
            # Add continent priority score to action value
            continent = get_target_continent(action, state)
            action_value += continent_scores[continent.name]

            # Prioritize border territories
            if get_territory(state.board, action.to_territory) in border_territories:
                action_value += 1

        # In PrePlace, prioritize only border territories
        elif state.turn_type == "PrePlace":
            continent = get_target_continent(action, state)
            action_value += continent_scores[continent.name]

            if get_territory(state.board, action.to_territory) in border_territories:
                action_value += 1

        # In Place, we want to be somewhat aggressive and place troops near enemy-owned territories
        elif state.turn_type == "Place":
            for neighbor in get_neighbors(state.board, action.to_territory):
                if state.owners[neighbor] != state.owners[get_territory(state.board, action.to_territory)]:
                    action_value += 0.5

        # Performs the default TurnInCards action
        elif state.turn_type == "TurnInCards":
            pass

        # Prioritize enemy territories where fewer other territories within the same continent are owned by that enemy
        elif state.turn_type == "Attack":
            # Simulate the action, get all possible successors
            successors, probabilities = simulateAction(state, action)
            for successor, probability in zip(successors, probabilities):
                # Each successor contributes its heuristic value * its probability to this action's value
                action_value += getReinforcementNum(successor, state.current_player)

        # Choose an action based on the amount of troops that action would take to execute.
        elif state.turn_type == "Occupy":
            action_value += action.troops

        # Fortify territories, prioritizing territories that border enemy territories.
        elif state.turn_type == "Fortify":
            if action.to_territory is None:
                action_value -= 1
            else:
                if not all(state.owners[n] == state.current_player for n in get_neighbors(state.board, action.to_territory)):
                    action_value += 1

        else:
            print("NOT A VALID STATE")

        scored_actions.append((action_value, action))

    # Return the best action
    return max(scored_actions)[1]

def get_territory(board, territory):
    """Return the territory in which an action would take place in a given board"""
    if type(territory) is int:
        return territory
    else:
        return board.territory_to_id[territory]

def get_neighbors(board, territory):
    """Return the neighbors of a given territory in a given board"""
    return board.territories[get_territory(board, territory)].neighbors

def get_target_continent(action, state):
    """Return the continent that an action would occur in, given a specific action and state"""
    return state.board.continents[get_continent_from_territory_ID(get_territory(state.board, action.to_territory))]

def get_player_controlling_continent(state, board, continent):
    """Returns the player ID that controls a continent, or -1 if no player controls every territory in that continent"""
    # Get territories in continent
    min_ID, max_ID = get_territory_IDs_from_continent(continent)

    # Check that all territories are owned by same player
    owner = state.owners[min_ID]
    for ID in range(min_ID + 1, max_ID + 1):
        # If a territory is owned by another player
        if state.owners[ID] != owner:
            return -1

    # Otherwise one player controls all territories
    return owner

def get_continent_from_territory_ID(territoryID):
    """Return the label of the continent where the given territoryID is found"""
    if territoryID <= 8:
        return "N. America"
    elif 8 < territoryID <= 12:
        return "S. America"
    elif 12 < territoryID <= 18:
        return "Africa"
    elif 18 < territoryID <= 25:
        return "Europe"
    elif 25 < territoryID <= 37:
        return "Asia"
    else:
        return "Australia"

def get_territory_IDs_from_continent(continent):
    """Return (min_ID, max_ID) tuple of territory ID range in given continent"""
    name = continent.name
    if name == "N. America":
        return (0, 8)
    elif name == "S. America":
        return (9, 12)
    elif name == "Africa":
        return (13, 18)
    elif name == "Europe":
        return (19, 25)
    elif name == "Asia":
        return (26, 37)
    else:
        return (38, 41)

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
