"""This module contains a number of functions for computing the heuristic
value of a state.

"""

import math

import utils

def percent_continents_owned(state):
    """Heuristic for percent continents owned.

    Holding entire continents is a strong feature in successful play. This
    function determines the averge percentage of continents owned.

    :param state: Game state to examine
    :type state: RiskState

    :returns: Average of percentages of territories owned per continent
    :rtype: float

    """

    value = 0.0
    
    continents = state.board.continents.values()

    for continent in continents:
        value += utils.continent_territories_held(state, continent)

    return value

def troop_standard_deviation(state):
    """Heuristic for distribution of troops.

    In general, we want troops to be reasonably evenly distributed across the
    board. This function computes the standard deviation of troops across all
    territories.

    :param state: Game state to examine
    :type state: RiskState

    :returns: Standard deviation for troops across the board
    :rtype: float

    """

    # First, we need to get the mean of troops per territory
    territories = state.board.territories
    troop_numbers = []

    # Get number of troops in each territory
    for territory in territories:
        terr_index = state.board.territory_to_id[territory.name]

        if state.owners[terr_index] == state.current_player:
            troop_numbers.append(state.armies[terr_index])

    # Case where we hold no territories
    if len(troop_numbers) == 0:
        return 0

    # Length of troop_numbers corresponds to number of territories
    average_troops = sum(troop_numbers) / len(troop_numbers)
    deviations = [(troops - average_troops)**2 for troops in troop_numbers]
    variance = sum(deviations) / len(deviations)
    standard_deviation = math.sqrt(variance)

    return standard_deviation

def percent_troops_wasted(state):
    """Heuristic for number of troops not in threatened territories.

    In general (and in current experience) it is not useful to have more than
    a single troop in a territory that is not threatened (i.e. has no neighbors
    owned by other players). This heuristic returns the proportion of troops
    that are "wasted" by not being on the frontlines compared to the total 
    number of troops.

    Based on discussion with Andrew LeFrance.

    :param state: State to examine
    :type state: RiskState

    :returns: Percentage of troops wasted
    :rtype: float

    """

    total_troops = 0.0
    wasted_troops = 0.0

    for territory in state.board.territories:
        terr_index = state.board.territory_to_id[territory.name]

        if state.owners[terr_index] == state.current_player:
            num_troops_in_territory = state.armies[terr_index]
            total_troops += num_troops_in_territory

            if not utils.is_threatened(state, territory):
                # Any troops after the first are "wasted" by being in an
                # unthreatened territory
                wasted_troops += num_troops_in_territory - 1

    if total_troops == 0:
        return 0

    return wasted_troops / total_troops

def easily_defended_continents(state):
    """Heuristic for improving hold on easily defended continents.

    Each continent grants a number of free troops per turn and has a number of
    borders to other continents from which an invasion could occur. Continents
    which grant a large number of free troops compared to their number of
    borders is generally easy to defend, thus we want to attempt to take such
    continents before their harder to defend counterparts.

    :param state: State to examine
    :type state: RiskState

    :returns: Value indicating the degree to which a state focuses on easily
              defended continents
    :rtype: float

    """

    defensibility = {}

    for continent in state.board.continents.values():
        troops_per_border = utils.continent_troops_per_border(state, continent)
        percent_held = utils.continent_territories_held(state, continent)
        defensibility[continent] = (troops_per_border, percent_held)

    value = 0.0
    weight = 1.0
    weight_decrement = 1.0 / len(defensibility.keys())
    
    # Based on answer to stackoverflow.com/questions/613183
    # particularly some of the comments
    for continent, values in sorted(defensibility.items(), key=lambda x: x[1]):
        value += weight * percent_held
        weight -= weight_decrement

    return value
        
def match_threatening_territories(state):
    """Try to at least match the number of enemy troops in bordering threat
    territories.

    Based on idea for defensive posture that came up during discussion with
    Adam Schwalm.

    :param state: State to examine
    :type state: RiskState

    :returns: Total number of troops we're short
    :rtype: float
    """

    value = 0.0

    for territory in state.board.territories:
        terr_index = state.board.territory_to_id[territory.name]

        if state.owners[terr_index] == state.current_player:
            num_troops_in_territory = state.armies[terr_index]

            for n in state.board.territories[terr_index].neighbors:
                if state.owners[n] != state.current_player:
                   if num_troops_in_territory <= state.armies[n]:
                      value -= (state.armies[n] - num_troops_in_territory)

    return value

def threatened_borders(state):
    """We generally want to minimize our threatened borders in order to provide
    opponents a smaller attack surface. This heuristic calculates the number
    of external, threatened borders.

    :param state: State to examine
    :type state: RiskState

    :returns: Total number of threatened borders
    :rtype: int

    """
    
    num_borders = 0
    
    for territory in state.board.territories:
        terr_index = state.board.territory_to_id[territory.name]
        if state.owners[terr_index] == state.current_player:
            for neighbor_id in territory.neighbors:
                if state.owners[neighbor_id] != state.current_player:
                    num_borders += 1
    
    return num_borders
    

    
        
        
