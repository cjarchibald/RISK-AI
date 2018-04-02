import random
from gui.aihelper import *
from gui.turbohelper import *
from risktools import *

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""

    #Get the possible actions in this state
    actions = getAllowedActions(state)

    #Select a Random Action
    myaction = random.choice(actions)
    highRatio = 0.0
    threshold = 2.0

    if state.turn_type == 'Attack':
        selectedAction = None
        #print "-----------"
        for a in actions:
            if selectedAction == None and a.to_territory == None:
                #print "set selected to None"
                selectedAction = a

            if a.to_territory != None:
                defender = state.board.territory_to_id[a.to_territory]
                attacker = state.board.territory_to_id[a.from_territory]
                numAttackers = state.armies[attacker]*1.0
                numDefenders = state.armies[defender]*1.0
                #print "attacker is",attacker,"w/",numAttackers,"defender is",defender,"w/",numDefenders
                if numDefenders > 0:
                    ratio = numAttackers/numDefenders
                    if ratio > threshold and ratio > highRatio:
                        highRatio = ratio
                        selectedAction = a
                        #print "attackers",numAttackers,"defenders",numDefenders,"ratio",ratio
        myaction = selectedAction
        #print "action is ",myaction.to_string()

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
