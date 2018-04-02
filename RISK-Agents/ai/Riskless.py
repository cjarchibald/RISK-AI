import random
from gui.aihelper import *
from risktools import *
from gui.turbohelper import *
import math
import Queue


# This is the function implement to implement an AI.
# Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""

    # Don't need to worry about time with this AI
    # if time_left is not None:
    # Decide how much time to spend on this decision

    # Get the possible actions in this state
    actions = getAllowedActions(state)
    player = state.current_player

    #print 'Heuristic AI : Player', state.players[state.current_player].name, 'considering', len(actions), state.turn_type, 'actions'

    myaction = random.choice(actions)

    # To keep track of the best action we find
    best_action = None
    best_action_value = None
    # Evaluate each action
    for a in actions:
        # If the turn type is TurnInCards, do the "thinking" here, because we had errors doing it in the heuristic fn.
        if a.type == "TurnInCards":
            # If all three cards have a value, that means we are turning in cards.
            # Always accept an action that turns in cards.
            if a.from_territory is not None and a.to_territory is not None and a.troops is not None:
                best_action_value = 10
                best_action = a
            # If we can't turn in cards, take whatever action given to us
            else:
                if best_action_value < 9:
                    best_action = a

        else:
            # For each action, compute that action's value in our current state.
            current_action_value = heuristic(state, a, player)

            # Store this as the best action if it is the first or better than what we have found
            if best_action_value is None or current_action_value > best_action_value:
                best_action = a
                best_action_value = current_action_value

    # Return the best action
    return best_action


def heuristic(state, a, player):
    """Returns a number telling how good this state is"""
    heur_number = -6

    # Go for N. and S. America and their borders at beginning of game, then go for neighboring countries
    if state.turn_type == "PreAssign":

        if a.to_territory is not None:
            # First take the territories that border N. and S. America.
            # This way we can defend our borders efficiently and also make it harder
            # for the opponent to take Europe, Africa, and Asia.
            if a.to_territory == "Kamchatka" or a.to_territory == "Iceland" or a.to_territory == "Western Africa":
                heur_number = 21
            elif state.board.territory_to_id[a.to_territory] in state.board.continents["N. America"].territories or state.board.territory_to_id[a.to_territory] in state.board.continents["S. America"].territories:
                heur_number = 20
            else:
                # Once all of N. and S. America claimed, take random territories.
                heur_number = random.randint(0, 19)
            if heur_number < 20:
                # Takes these key territories if possible after N. and S. America
                if a.to_territory == "Indonesia":
                    heur_number = 20
                if a.to_territory == "Middle East":
                    heur_number = 19

    # Decides where to place our reinforcements at the beginning of the game.
    elif state.turn_type == "PrePlace":

        # Stack the border territories of N. America after we have secured the continent
        enemy_armies = 0
        for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
            if state.owners[n] != player:
                enemy_armies += state.armies[n]
        if (a.to_territory == "Iceland" or a.to_territory == "Western Africa" or a.to_territory == "Kamchatka") and state.armies[state.board.territory_to_id[a.to_territory]] < enemy_armies + 2:
            heur_number = 10 * (enemy_armies / state.armies[state.board.territory_to_id[a.to_territory]])

        # First places we are putting reinforcements are N. and S. America.
        # The stackContinent function also takes care of randomizing where to put troops after
        # N. and S. America are secured.
        heur_number = stackContinent("N. America", a, state, heur_number, player)
        if heur_number < 12:
            heur_number = stackContinent("S. America", a, state, heur_number, player)
        if a.to_territory == "Mexico" or a.to_territory == "Colombia":
            heur_number -= 1

    elif state.turn_type == "Attack":

        # First check and see if they have any continents.  Will use this info later.
        enemy_continents = []
        for p in state.players:
            if p.id != state.current_player:
                enemy_continents.extend(getContinentsOwned(state, p.id))

        # If the action is an attack:
        if a.to_territory is not None:
            # This provides a small but important boost to any attack that can start a chain of attacks.
            if neighborIsOwned(state.board.territory_to_id[a.to_territory], state, player, "opp"):
                if state.armies[state.board.territory_to_id[a.from_territory]] >= state.armies[state.board.territory_to_id[a.to_territory]] * 2:
                    heur_number = 1

            # Find the territory that will be easiest to take.
            unownedNAmer = unownedTerritoriesInContinent("N. America", state, player)
            unownedSAmer = unownedTerritoriesInContinent("S. America", state, player)
            unownedEur = unownedTerritoriesInContinent("Europe", state, player)
            unownedAfr = unownedTerritoriesInContinent("Africa", state, player)
            unownedAsia = unownedTerritoriesInContinent("Asia", state, player)
            unownedAus = unownedTerritoriesInContinent("Australia", state, player)
            attackForceNAmer = calcAttackForce(unownedNAmer, state)
            attackForceSAmer = calcAttackForce(unownedSAmer, state)
            attackForceEur = calcAttackForce(unownedEur, state)
            attackForceAfr = calcAttackForce(unownedAfr, state)
            attackForceAsia = calcAttackForce(unownedAsia, state)
            attackForceAus = calcAttackForce(unownedAus, state)

            # Given the info just computed, get the order in which to attack the continents.
            continent_names = pickContinent(attackForceEur, attackForceAfr, attackForceAsia, attackForceAus, attackForceNAmer, attackForceSAmer)

            # Cycle through every continent, with a steadily decreasing priority.
            priority = 24
            for cont in continent_names:

                # Get the clusters of contiguous territories in the continent
                clusters = getTerritoryClusters(unownedTerritoriesInContinent(cont, state, player), state)

                # These two big if statements make sure that N. and S. America are treated as one continent.
                # This way, an attack can flow from N. America into S. America smoothly.
                if cont == "N. America":
                    clusters_south = getTerritoryClusters(unownedTerritoriesInContinent("S. America", state, player), state)
                    for c in clusters:
                        if state.board.territory_to_id["Mexico"] in c:
                            for c_south in clusters_south:
                                if state.board.territory_to_id["Colombia"] in c_south:
                                    c.extend(c_south)
                if cont == "S. America":
                    clusters_north = getTerritoryClusters(unownedTerritoriesInContinent("N. America", state, player), state)
                    for c in clusters:
                        if state.board.territory_to_id["Colombia"] in c:
                            for c_north in clusters_north:
                                if state.board.territory_to_id["Mexico"] in c_north:
                                    c.extend(c_north)

                # Sort the territory clusters longest to shortest, and cycle through them, with decreasing priority.
                clusters = sortByLength(clusters)
                priority_cl = 4
                for cl in clusters:

                    # Find which territory should be our attack target, and where to attack from in order
                    # to follow a path that will let us take the entire cluster in one run.
                    attackFrom, attackTo = findAttackPoint(cl, cont, state, player)

                    # If the given action matches what we just found:
                    if attackFrom == state.board.territory_to_id[a.from_territory] and attackTo == state.board.territory_to_id[a.to_territory]:
                        # Attack if we feel we can beat them, and if we have at least 3 troops in the country.
                        if state.armies[attackFrom] >= state.armies[attackTo]:
                            heur_number = 20 + priority + priority_cl
                        else:
                            heur_number = -1
                    priority_cl -= 1

            # This block preserves our defense of N. and S. America,
            if a.from_territory == "Kamchatka" or a.from_territory == "Western Africa" or a.from_territory == "Iceland":
                # but if we have more than 9 in the territory,
                if state.armies[state.board.territory_to_id[a.from_territory]] < 7:
                    # or we are attacking N. or S. America, let the attack happen by not activating the -10.
                    if state.board.territory_to_id[a.to_territory] not in state.board.continents["N. America"].territories:
                        if state.board.territory_to_id[a.to_territory] not in state.board.continents["S. America"].territories:
                            heur_number = -10

            # If enemy has a full continent, disrupt it
            if len(enemy_continents) > 0:

                # Find the biggest threat
                max_value = 0
                target_continent = ""
                for c in enemy_continents:
                    if state.board.continents[c].reward > max_value:
                        target_continent = c
                        max_value = state.board.continents[c].reward

                # Once we have the biggest threat, find the weakest link in their defenses, and target it.
                HQ, target = findWeakLink(target_continent, state, player)

                # Make sure this gets done if the situation presents itself.
                if state.board.territory_to_id[a.from_territory] == HQ and state.board.territory_to_id[a.to_territory] == target:
                    heur_number = 100
            priority -= 4
        else:
            # This allows for us not to attack if we don't want to.
            heur_number = 0

    # Find the territory that has the most troops not bordering an enemy, and move those troops
    # towards the nearest enemy.
    elif state.turn_type == "Fortify":
        if a.to_territory != None:
            if not neighborIsOwned(state.board.territory_to_id[a.from_territory], state, player, "opp"):
                enemy_path = goToNearestEnemy(state.board.territory_to_id[a.from_territory], state, player)
                if state.board.territory_to_id[a.to_territory] == enemy_path and a.troops == state.armies[state.board.territory_to_id[a.from_territory]] - 1:
                    heur_number = 20 * a.troops
            if neighborIsOwned(state.board.territory_to_id[a.to_territory], state, player, "opp") and a.troops == state.armies[state.board.territory_to_id[a.from_territory]] - 1:
                    heur_number = 21 * a.troops

            # Do not fortify out of our border territories unless they are not bordering an enemy,
            if a.from_territory == "Kamchatka" or a.from_territory == "Western Africa" or a.from_territory == "Iceland":
                if neighborIsOwned(state.board.territory_to_id[a.from_territory], state, player, "opp"):
                    heur_number = -1
        else:
            heur_number = 0

    # Move all possible troops to occupied territory
    elif state.turn_type == "Occupy":
        if a.from_territory != None and a.to_territory != None:
            if a.troops == state.armies[state.board.territory_to_id[a.from_territory]] - 1:
                heur_number = 10
            else:
                heur_number = 0

            # Unless we are moving a significant number of troops, only move one troop from a border territory.
            if a.from_territory == "Kamchatka" or a.from_territory == "Western Africa" or a.from_territory == "Iceland":
                if a.troops > 1 and a.troops < 10:
                    heur_number = -1
                else:
                    heur_number = 0
        else:
            heur_number = 0

    # Determins where to place our troops in order to give the attack algorithm the best chance of succeeding.
    elif state.turn_type == 'Place':

        # First check and see if they have any continents
        enemy_continents = []
        for p in state.players:
            if p.id != state.current_player:
                enemy_continents.extend(getContinentsOwned(state, p.id))

        # A backup plan in case all of the following is completed.  Place troops on borders.
        if neighborIsOwned(state.board.territory_to_id[a.to_territory], state, player, "opp"):
            heur_number = 1

        # Using the same logic as attack to pick the continent order.
        unownedNAmer = unownedTerritoriesInContinent("N. America", state, player)
        unownedSAmer = unownedTerritoriesInContinent("S. America", state, player)
        unownedEur = unownedTerritoriesInContinent("Europe", state, player)
        unownedAfr = unownedTerritoriesInContinent("Africa", state, player)
        unownedAsia = unownedTerritoriesInContinent("Asia", state, player)
        unownedAus = unownedTerritoriesInContinent("Australia", state, player)
        attackForceNAmer = calcAttackForce(unownedNAmer, state)
        attackForceSAmer = calcAttackForce(unownedSAmer, state)
        attackForceEur = calcAttackForce(unownedEur, state)
        attackForceAfr = calcAttackForce(unownedAfr, state)
        attackForceAsia = calcAttackForce(unownedAsia, state)
        attackForceAus = calcAttackForce(unownedAus, state)
        continents = pickContinent(attackForceEur, attackForceAfr, attackForceAsia, attackForceAus, attackForceNAmer, attackForceSAmer)

        # Cycle through the continents with a progressively decreasing priority.
        priority = 12
        for cont in continents:
            heur_number = stackContinent(cont, a, state, heur_number, player)
            heur_number += priority
            priority -= 2

        # This lets the traditional border territories of N. and S. America replace our optimal
        # border territories if we don't own the better ones.
        unowned_border = []
        if state.owners[state.board.territory_to_id["Kamchatka"]] != player:
            if a.to_territory == "Alaska" and "N. America" in getContinentsOwned(state, player):
                unowned_border.append(state.board.territory_to_id["Kamchatka"])
                if state.armies[state.board.territory_to_id["Alaska"]] < calcAttackForce(unowned_border, state):
                    heur_number = 31
        elif state.owners[state.board.territory_to_id["Iceland"]] != player:
            if a.to_territory == "Greenland" and "N. America" in getContinentsOwned(state, player):
                unowned_border.append(state.board.territory_to_id["Iceland"])
                if state.armies[state.board.territory_to_id["Greenland"]] < calcAttackForce(unowned_border, state):
                    heur_number = 31
        elif state.owners[state.board.territory_to_id["Western Africa"]] != player:
            if a.to_territory == "Brazil" and "S. America" in getContinentsOwned(state, player):
                unowned_border.append(state.board.territory_to_id["Western Africa"])
                if state.armies[state.board.territory_to_id["Brazil"]] < calcAttackForce(unowned_border, state):
                    heur_number = 31

        # Makes sure our borders always have at least 4 more troops than the total number of surrounding enemy troops.
        if a.to_territory == "Kamchatka" or a.to_territory == "Iceland" or a.to_territory == "Western Africa":
            enemy_armies = 0
            for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                if state.owners[n] != player:
                    enemy_armies += state.armies[n]
            if state.armies[state.board.territory_to_id[a.to_territory]] < enemy_armies + 4:
                heur_number = 30

        # Avoid placing troops on non-border territories.
        if not neighborIsOwned(state.board.territory_to_id[a.to_territory], state, player, "opp"):
            heur_number = -1

        # If enemy has a full continent, disrupt it
        if len(enemy_continents) > 0:
            # Find the biggest threat
            max_value = 0
            target_continent = ""
            for c in enemy_continents:
                if state.board.continents[c].reward >= max_value:
                    target_continent = c
                    max_value = state.board.continents[c].reward
            HQ, target = findWeakLink(target_continent, state, player)
            if state.board.territory_to_id[a.to_territory] == HQ and state.armies[HQ] < calcAttackForce([target], state):
                heur_number = 1000

    return heur_number

# Finds the weakest spot in an enemy continent, and where to attack it from.
def findWeakLink(target_continent, state, player):
    borders = getContinentBorders(target_continent, state, "ID")
    weak_points = []
    weakest_link = 1000
    for b in borders:
        if state.armies[b] <= weakest_link:
            if state.armies[b] < weakest_link:
                weak_points = []
                weakest_link = state.armies[b]
            weak_points.append(b)
    best_ratio = 0.0
    best_HQ = None
    best_target = None
    for terr in weak_points:
        for n in state.board.territories[terr].neighbors:
            if state.owners[n] == player:
                if (state.armies[n] / state.armies[terr]) > best_ratio:
                    best_ratio = state.armies[n] / state.armies[terr]
                    best_HQ = n
                    best_target = terr
    if len(state.board.players) == 2:
        if state.board.players[0].id == player:
            enemy = state.board.players[1].id
        else:
            enemy = state.board.players[0].id
        if best_HQ is None:
            shortest_path = 1000
            for terr in weak_points:
                junk, path = goToNearestEnemy(terr, state, enemy)
                if len(path) < shortest_path:
                    shortest_path = len(path)
                    best_target = path[len(path) - 1]
                    max_troops = 0
                    for n in state.board.territories[best_target].neighbors:
                        if state.owners[n] == player and state.armies[n] > max_troops:
                            best_HQ = n
    return best_HQ, best_target


# This returns the territory ID of the territory neighboring the given territory which is closest to an enemy,
# and the path used to get there.  Returns None if you are already at a border
def goToNearestEnemy(territory, state, player):
    checked = [territory]
    queue = []
    for t in state.board.territories[territory].neighbors:
        terrPath = []
        terrPath.append(t)
        terrPath.append(t)
        queue.append(terrPath)
    while len(queue) != 0:
        current = queue[0]
        queue.remove(queue[0])
        checked.append(current[0])
        if neighborIsOwned(current[0], state, player, "opp"):
            return current[1], checked
        for n in state.board.territories[current[0]].neighbors:
            if n not in checked:
                terrPath1 = []
                terrPath1.append(n)
                terrPath1.append(current[1])
                queue.append(terrPath1)

# Distributes troops among any enemy clusters, placing enough territories at each cluster to have
# a 90% certainty of conquering it.
def stackContinent(continent_name, a, state, heur_number, player):

    # Gets all the clusters of enemy territories in the given continent.
    clusters = getTerritoryClusters(unownedTerritoriesInContinent(continent_name, state, player), state)

    # These two big if statements make sure that N. and S. America are treated as one continent.
    # This way, an attack can flow from N. America into S. America smoothly.
    if continent_name == "N. America":
        clusters_south = getTerritoryClusters(unownedTerritoriesInContinent("S. America", state, player), state)
        for c in clusters:
            if state.board.territory_to_id["Mexico"] in c:
                for c_south in clusters_south:
                    if state.board.territory_to_id["Colombia"] in c_south:
                        c.extend(c_south)
    if continent_name == "S. America":
        clusters_north = getTerritoryClusters(
            unownedTerritoriesInContinent("N. America", state, player), state)
        for c in clusters:
            if state.board.territory_to_id["Colombia"] in c:
                for c_north in clusters_north:
                    if state.board.territory_to_id["Mexico"] in c_north:
                        c.extend(c_north)

    # If there is only one cluster of unconquered territories, find the optimum attack point,
    # and place enough armies there to make sure we take the cluster.
    if len(clusters) == 1:
        attackHQ, attackPoint = findAttackPoint(clusters[0], continent_name, state, player)
        if state.armies[attackHQ] < calcAttackForce(clusters[0], state):
            to_terr = state.board.territory_to_id[a.to_territory]
            if attackHQ == to_terr:
                #This lets troops be evenly distributed among the various clusters.
                heur_number = 10 * ((calcAttackForce(clusters[0], state)) / state.armies[attackHQ])

    # If there is more than one cluster, place enough armies for the biggest cluster first,
    # then try to take smaller clusters.
    elif len(clusters) > 1:
        # sort the clusters by size
        sorted_clusters = sortByLength(clusters)
        attack_points = []
        for c in sorted_clusters:
            attackHQ, attackPoint = findAttackPoint(c, continent_name, state, player, attack_points)
            attack_points.append(attackHQ)
            if state.board.territory_to_id[a.to_territory] == attackHQ and state.armies[attackHQ] < calcAttackForce(clusters[0], state):
                heur_number = 10 * (calcAttackForce(c, state) / state.armies[attackHQ])

    # If none of the previous have been activated:
    if heur_number == -6:
        continents_owned = getContinentsOwned(state, player)
        # Avoids placing troops in continents we already own.
        if isInContinents(state.board.territory_to_id[a.to_territory], continents_owned, state) or state.board.territory_to_id[a.to_territory] in state.board.continents[continent_name].territories:
            heur_number = -1
        else:
            # Randomly places troops on border territories.
            heur_number = random.randint(1, 11)
    return heur_number


# Receives a territory ID and a list of continent names.
# Returns True if the given territory is in any of the continents, False otherwise.
def isInContinents(territory, continent_list, state):
    for cont in continent_list:
        if territory in state.board.continents[cont].territories:
            return True
    return False


# Returns a list of continents owned entirely by the given player
def getContinentsOwned(state, player):
    continents_owned = ["N. America", "S. America", "Europe", "Africa", "Asia", "Australia"]
    for cont in state.board.continents:
        for terr in state.board.continents[cont].territories:
            if state.owners[terr] != player:
                if cont in continents_owned:
                    continents_owned.remove(cont)
    return continents_owned

# Returns a list of continent names, ordered by attack priority.
# Americas first, then the one with the smallest attack force.
def pickContinent(attackForceEur, attackForceAfr, attackForceAsia, attackForceAus, attackForceNAmer, attackForceSAmer):
    continent_order = [["N. America", attackForceNAmer], ["S. America", attackForceSAmer], ["Africa", attackForceAfr],  ["Europe", attackForceEur],  ["Asia", attackForceAsia],  ["Australia", attackForceAus]]
    l = 0
    while l < 5:
        r = l + 1
        while r < 6:
            if continent_order[r][1] < continent_order[l][1]:
                if not ((continent_order[l][0] == "N. America" and continent_order[r] != "S. America") or (continent_order[l][0] == "S. America" and continent_order[r] != "N. America")):
                    temp = continent_order[l]
                    continent_order[l] = continent_order[r]
                    continent_order[r] = temp
            r += 1
        l += 1
    final_order = []
    for i in continent_order:
        if i[1] > 0:
            final_order.append(i[0])
    return final_order

# Sorts the given list by size.  Returns the sorted list.
def sortByLength(list):
    l = 0
    if len(list) == 1:
        return list
    while l < len(list) - 1:
        r = l + 1
        while r < len(list):
            if len(list[l]) < len(list[r]):
                temp = list[l]
                list[l] = list[r]
                list[r] = temp
            r += 1
        l += 1
        return list


# Takes the name of the continent in string format.  Returns a list of border territory names.
# If given a second parameter "ID" it will return territory IDs.
def getContinentBorders(continent, state, format="Name"):
    borders = []
    # N. and S. America are modified to make them act like one continent.
    if (continent == "N. America"):
        borders.append("Alaska")
        borders.append("Greenland")
        borders.append("Brazil")
    elif (continent == "S. America"):
        borders.append("Brazil")
    elif (continent == "Europe"):
        borders.append("Iceland")
        borders.append("Ukraine")
        borders.append("Southern Europe")
        borders.append("Western Europe")
    elif (continent == "Africa"):
        borders.append("Ethiopia")
        borders.append("Western Africa")
        borders.append("Egypt")
    elif (continent == "Asia"):
        borders.append("Middle East")
        borders.append("Pakistan")
        borders.append("Russia")
        borders.append("Laos")
        borders.append("Kamchatka")
        borders.append("Laos")
    elif (continent == "Australia"):
        borders.append("Indonesia")
    if format == "ID":
        for t in range(len(borders)):
            borders[t] = state.board.territory_to_id[borders[t]]
    return borders


# This function tells you what countries you don't own in a certain continent.
# Returns a list of territory ids.
def unownedTerritoriesInContinent(continent_name, state, player):
    unowned = []
    # Loop through territories in the continent
    for territory_in_continent in state.board.continents[continent_name].territories:
        # if owner of territory is not us
        if state.owners[territory_in_continent] != player:
            # add to list of unowned territories
            unowned.append(territory_in_continent)
    return unowned


# This function receives a list of territory ids that may or may not border each other,
# and returns a list in which each element is a list of territories which border each other.
# The original list may contain only one set of contiguous territories, or it may contain several.
# Returns a list of lists of territory ids.
def getTerritoryClusters(territories, state):
    territory_list = territories
    clusters = []
    # Loops until all territories accounted for
    while len(territory_list) > 0:
        # list of contiguous territories
        bordering = []
        bordering.append(territory_list[0])
        territory_list.remove(territory_list[0])
        itemsAdded = []
        for t in territory_list:
            if listOverlap(state.board.territories[t].neighbors, bordering):
                bordering.append(t)
                itemsAdded.append(t)
        for i in itemsAdded:
            territory_list.remove(i)
        clusters.append(bordering)
    return clusters


# Returns true is there is any overlap in the lists.
def listOverlap(list1, list2):
    for elem1 in list1:
        for elem2 in list2:
            if elem1 == elem2:
                return True
    return False


# This function receives a cluster of bordering territories and returns the number of armies needed
# to be fairly sure of conquering the entire cluster in one turn.
# Return format: integer
def calcAttackForce(territory_list, state):
    if len(territory_list) == 0:
        return 0
    armies_needed = 0
    # bool to check if more than one country is invaded
    more_than_one = False
    # Loop through territories in the cluster
    for territory_in_cluster in territory_list:
        # print "In for loop"
        # add to armies needed
        armies_needed += state.armies[territory_in_cluster] * 2.8
        # adds 1 if for each territory after the first
        if more_than_one:
            armies_needed += 1
        else:
            more_than_one = True
    # round up, minimum of 4, and return
    if armies_needed < 4:
        armies_needed = 4
    armies_needed = int(math.ceil(armies_needed))
    return armies_needed


# This receives a cluster of enemy territories and calculates the optimal attack point.
# It returns two things, the territory ID of the first territory in the cluster to attack,
# and the territory ID of the territory we are attacking from.
# continent_name is the string name of the continent we are in.  It is needed for calculations.
def findAttackPoint(cluster, continent_name, state, player, used = []):

    # The first country to be attacked
    firstVictim = 0
    # Where to attack from
    attackHQ = 0

    # In order to find which territory to attack first, we need to find the path that starts
    # on one end of the cluster and finishes on a territory which is either a border
    # territory (from getContinentBorders) or is one step away from a border territory.

    # We also need to consider which of our territories has the most troops already in it.
    # That will factor in to our decision on where to mass our attack force.

    # Find which node to end on
    ending_node = getEndingNode(continent_name, cluster, state, player)

    # Using that info, find a list of possible start nodes that would let you conquer the whole
    # cluster in one turn.
    starting_nodes = []
    findStartTerritories(cluster, ending_node, [], starting_nodes, state, player)

    # Find which start territory has the node with the most troops nearest to it.
    max_troops = 0
    possible_victims = []
    possible_HQs = []
    for t in starting_nodes:
        for n in state.board.territories[t].neighbors:
            if state.armies[n] >= max_troops and state.owners[n] == player:
                if n not in used:
                    if state.armies[n] > max_troops:
                        possible_victims = []
                        possible_HQs = []
                    max_troops = state.armies[n]
                    possible_victims.append(t)
                    possible_HQs.append(n)

    # Make sure we attack from inside the continent we are trying to take, if possible.
    if len(possible_victims) > 0:
        removing = []
        for i in range(len(possible_victims)):
            if possible_HQs[i] not in state.board.continents[continent_name].territories:
                if (len(possible_HQs) - len(removing)) > 1:
                    removing.append(i)
        popped = 0
        for j in removing:
            junk = possible_HQs.pop(j - popped)
            junk = possible_victims.pop(j - popped)
            popped += 1
        attackHQ = possible_HQs[0]
        firstVictim = possible_victims[0]

    return attackHQ, firstVictim


# Depth-first-search to find the path from the ending_node to the node we will first attack.
def findStartTerritories(cluster, start_node, terr_seen, possible_end_territories, state, player):
    terr_seen.append(start_node)
    neighbors_list = []
    for ter in state.board.territories[start_node].neighbors:
        neighbors_list.append(ter)
    removing = []
    for n in neighbors_list:
        if n in terr_seen:
            removing.append(n)
        if n not in cluster:
            removing.append(n)
    for r in removing:
        neighbors_list.remove(r)
    # If there are no territories in start_node.neighbors that are in the cluster and not also in terr_seen,
    if len(neighbors_list) == 0:
        if (len(terr_seen) == len(cluster)) and neighborIsOwned(start_node, state, player):
            possible_end_territories.append(start_node)
    else:
        for n in neighbors_list:
            if n not in terr_seen:
                findStartTerritories(cluster, n, terr_seen, possible_end_territories, state, player)
    terr_seen.remove(start_node)
    return


# Returns true if any of the given territories neighbors are owned by the current player.
def neighborIsOwned(terr, state, player, owner="player"):
    for t in state.board.territories[terr].neighbors:
        if owner == "player":
            if state.owners[t] == player:
                return True
        else:
            if state.owners[t] != player:
                return True
    return False


# Finds the node that we need to end our attack at.
def getEndingNode(continent_name, cluster, state, player):
    # Check if any nodes in cluster are border nodes
    border_nodes = []
    ending_node = -1
    borders = getContinentBorders(continent_name, state, "ID")
    for t in cluster:
        if t in borders:
            border_nodes.append(t)
    # If any nodes are borders, decide between them
    if len(border_nodes) == 1:
        ending_node = border_nodes[0]
    elif len(border_nodes) > 1:
        # Choose the border node that is bordering an enemy
        for t in border_nodes:
            for n in state.board.territories[t].neighbors:
                if state.owners[n] != player:
                    ending_node = t

    # No border territories in cluster, are any territories in cluster bordering a border territory?
    else:
        for t in cluster:
            if listOverlap(state.board.territories[t].neighbors, borders):
                ending_node = t

    # Last resort, pick the first one.
    if ending_node == -1:
        for t in cluster:
            if neighborIsOwned(t, state, player):
                ending_node = cluster[0]
    return ending_node


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
