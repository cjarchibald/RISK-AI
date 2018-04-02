"""This module contains a number of utility functions to aid the heuristic
functions in the heuristics module.

"""

def is_threatened(state, territory):
    """Return true if territory is threatened.

    :param state: State being examined
    :type state: RiskState
    :param territory: Territory to inspect
    :type territory: RiskTerritory

    :returns: True if territory is threatened (has a border with non-owned
              territory)
    :rtype: bool

    """

    for neighbor_id in territory.neighbors:
        # One of the neighbor territories is not owned so territory is
        # threatened
        if state.owners[neighbor_id] != state.current_player:
            return True
    else:
        return False

def continent_territories_held(state, continent):
    """Find the percentage of territories we hold for a given continent.

    :param state: State being examined
    :type state: RiskState
    :param continent: Continent to find number of territories held in
    :type continent: RiskContinent

    :returns: Percentage of territories held in a continent
    :rtype: float

    """

    num_owned = 0

    for terr_id in continent.territories:
        if state.owners[terr_id] == state.current_player:
            num_owned += 1

    return float(num_owned) / len(continent.territories)

def continent_num_borders(state, continent):
    """Find the number of borders with other continents for a continent.

    :param state: State being examined
    :type state: RiskState
    :param continent: Continent to inspect
    :type continent: RiskContinent

    :returns: Number of borders with other continents
    :rtype: int

    """

    # Get the territory objects for each territory in contintent
    continent_territories = []
    
    for territory in state.board.territories:
        terr_id = state.board.territory_to_id[territory.name]
        if terr_id in continent.territories:
            continent_territories.append(territory)

    # Roll over each 
    num_borders = 0
    for territory in continent_territories:
        for neighbor_id in territory.neighbors:
            # Must be an edge to another continent
            if neighbor_id not in continent.territories:
                num_borders += 1

    return num_borders

def continent_troops_per_border(state, continent):
    """Find the number of free troops per external border for a continent.

    A simple way to tell if a continent is good to attempt to take is the
    number of free troops granted per border territory. For example, in the
    default RISK game, Australia grants 2 free troops but has only a single
    border, thus the continent grants 2 troops per border. This makes it a
    strong contender. North America is also good.

    Based on heuristic suggested by RISK paper/Analysis article (see references
    in paper)

    :param state: State to examine
    :type state: RiskState
    :param continent: Continent to compute troops per border for
    :type continent: RiskContinent

    :returns: Free troops per external border
    :rtype: float
    
    """

    free_troops = continent.reward
    num_borders = continent_num_borders(state, continent)

    return float(free_troops) / num_borders

