import random
from gui.aihelper import *
from risktools import *
from gui.turbohelper import *

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""

    actions = getAllowedActions(state)

    #print 'Heuristic AI : Player', state.players[state.current_player].name, 'considering', len(actions), 'actions'
    curr_player = state.current_player

    #To keep track of the best action we find
    best_action = None
    best_action_value = None

    #Evaluate each action
    for a in actions:
        #Simulate the action, get all possible successors
        successors, probabilities = simulateAction(state, a)

        #Compute the expected heuristic value of the successors
        current_action_value = 0.0

        for i in range(len(successors)):
            #Each successor contributes its heuristic value * its probability to this action's value
            current_action_value += (heuristic(successors[i], curr_player, a) * probabilities[i])

        #Store this as the best action if it is the first or better than what we have found
        if best_action_value is None or current_action_value > best_action_value:
            best_action = a
            best_action_value = current_action_value

    #Return the best action
    return best_action

def heuristic(state, our_ai, action):
    # print("\n")
    #print(our_ai)
    #print(state.turn_type)
    h = 0

    if state.turn_type == 'PreAssign' :
        total = 0

        #Generate list of owned territory ids
        owned = []
        for i in range(len(state.owners)):
            if our_ai == state.owners[i]:
                owned.append(i)

        #Add preference to territories with friendly neighbors
        #to increase likelihood of clustering
        for i in owned:
            t = state.board.territories[i]
            for nb in t.neighbors:
                if state.owners[nb] == our_ai:
                    total += 1

        #Give preference to austrialian territories during
        #placement
        for terr in state.board.continents["Australia"].territories:
            if state.board.territories[terr].name == action.to_territory:
                total += 75

        #Give preference to S. American territories during
        #placement
        for terr in state.board.continents["S. America"].territories:
            if state.board.territories[terr].name == action.to_territory:
                total += 100

        h = total

    if state.turn_type == "Occupy":
        h = state.armies[state.last_defender]

    if state.turn_type == 'Fortify' or state.turn_type == 'Place' or state.turn_type == 'PrePlace':
        total = 0

        #Generate list of owned territory ids
        owned = []
        for i in range(len(state.owners)):
            if our_ai == state.owners[i]:
                owned.append(i)

        #Iterate over owned and up the ratio of our states armies
        #vs our enemy neighbor's armies and our enemy neighbor's
        #neighbor's armies
        for i in owned:
            t = state.board.territories[i]
            for nb in t.neighbors:
                if state.owners[nb] != our_ai:
                    total += state.armies[i]/state.armies[nb]
                    for nb2 in state.board.territories[nb].neighbors:
                        if state.owners[nb2] != our_ai:
                            total += state.armies[i]/state.armies[nb2]
                            for nb3 in state.board.territories[nb2].neighbors:
                                if state.owners[nb3] != our_ai:
                                    total += state.armies[i]/state.armies[nb3]

        h = total

    if state.turn_type == "TurnInCards":
        h = state.players[our_ai].free_armies

    if state.turn_type == 'Attack':

        #Read in the settings file for the weights
        army_weight = 733
        owned_weight = 292
        rein_weight = 370
        battle_weight = 809
        reward_weight = 783

        for player in state.players:
            total = 0

            #Generate List of owned territory ids
            owned = []
            for i in range(len(state.owners)):
                if player.id == state.owners[i]:
                    owned.append(i)

            #Add up total armies
            for i in owned:
                total += state.armies[i]*army_weight

            #Add up number of owned countries
            total += len(owned)*owned_weight

            #Add up reinforcment numbers
            total += getReinforcementNum(state,player)*rein_weight

            #Look through owned territories and add up the ratios
            #of that army vs it's opponents
            for i in owned:
                t = state.board.territories[i]
                for nb in t.neighbors:
                    if state.owners[nb] != player.id:
                        total += battle_weight*state.armies[i]/state.armies[nb]

            #Iterate over continents to determine if they are owned
            #and apply reward
            for continent in state.board.continents.itervalues():
                if set(continent.territories) <= set(owned):
                    total += reward_weight*continent.reward

            #If this was our player, add the total heuristic value
            if player.id == our_ai:
                h += total
            #Otherwise subtract it
            else:
                h -= total

    return h

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
