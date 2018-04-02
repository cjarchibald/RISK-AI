import gui.riskengine
import gui.riskgui
import random
from gui.aihelper import *
from gui.turbohelper import *
from risktools import *

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    

    PrePlace_Order = ['Eastern Australia','Western Australia','New Guinea','Indonesia','Laos','China','Manchuria','Japan','Irkutsk','Kamchatka','Eastern Russia','Alaska','Inktitut','British Columbia','Ontario','Quebec','Greenland','Western U.S.','Eastern U.S.','Mexico','India','Siberia','Russia','Pakistan','Middle East','Ukraine','Sweden','Central Europe','Southern Europe','Western Europe','Great Britan','Iceland','Colombia','Peru','Brazil','Chile','Western Africa','Egypt','Ethiopia','Zaira','South Africa','Madagascar']
    #Get the possible actions in this state
    actions = getAllowedActions(state)

    #name = {}
    #name = 
    #print(name)
        
    #Select a Random Action
    myaction = random.choice(actions)

    #print("Peace Agent : I want to make the world peace again!")

    if state.turn_type == 'PreAssign':

        PrePlace_Actions = []
        c = 0

        for s in PrePlace_Order:
            for a in actions:
                if(s == a.to_territory and c == 0):
                    #for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                     #   if state.owners[n] != state.current_player:
                    #PrePlace_Actions.append(a)
                    myaction = a
                    c+=1
                    #print("Pre Place taken frome here")
    
    if state.turn_type == 'Attack':
        possible_actions = []
        ratios = []
        for a in actions:
            if a.to_territory is not None and a.from_territory is not None:
                if(state.armies[state.board.territory_to_id[a.from_territory]] > state.armies[state.board.territory_to_id[a.to_territory]]):
                    possible_actions.append(a)
                    ratios.append(state.armies[state.board.territory_to_id[a.from_territory]]/state.armies[state.board.territory_to_id[a.to_territory]])
        if len(possible_actions)>0:
            Max = 0
            for r in ratios:
                if Max<r:
                    Max = r
            for a in actions:
                c = state.armies[state.board.territory_to_id[a.from_territory]]/state.armies[state.board.territory_to_id[a.to_territory]]
                if Max == c:
                    #print("Attacking from ", a.from_territory, "with ", state.armies[state.board.territory_to_id[a.from_territory]], "To ", a.to_territory, "Have ", state.armies[state.board.territory_to_id[a.to_territory]])
                    myaction = a
                    break
        #print("Attacking--------->",myaction.from_territory,myaction.to_territory,state.armies[state.board.territory_to_id[myaction.to_territory]])
    '''
    if state.turn_type == 'PrePlace':

        PrePlace_Actions = []

        for s in PrePlace_Order:
            for a in actions:
                if(s == a.to_territory):
                    #for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                     #   if state.owners[n] != state.current_player:
                    PrePlace_Actions.append(a)
        myaction = PrePlace_Actions[0]
    '''    
    if state.turn_type == 'PrePlace':
        possible_actions = []

        for a in actions:
            if a.to_territory is not None:
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        #print("Owners",state.owners[n],state.current_player)
                        possible_actions.append(a)
                    
        if len(possible_actions) > 0:
            myaction = random.choice(possible_actions)
    
    '''
    if state.turn_type == 'Occupy':
        for a in actions:
            print("----------------------------------------->",a.troops)
    '''

    if state.turn_type == 'Place':
        possible_actions = []
        pos1 = []
        pos2 = []
        pos3 = []
        pos4 = []

        for a in actions:
            if a.to_territory is not None:
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    #print("N",n,a.to_territory,a.troops)
                    if state.owners[n] != state.current_player:
                        #print("Owners",state.owners[n],state.current_player)
                        #possible_actions.append(a)
                        if state.armies[n] > (state.armies[state.board.territory_to_id[a.to_territory]]):
                            pos3.append(a)
                        elif state.armies[n] < (state.armies[state.board.territory_to_id[a.to_territory]]):
                            if state.armies[state.board.territory_to_id[a.to_territory]]/state.armies[n] > 1.75:
                                pos1.append(a)
                                #print(state.armies[state.board.territory_to_id[a.to_territory]]/state.armies[n])
                            else:
                                pos2.append(a)
                        else:
                            pos4.append(a)
                    
        if len(pos1) > 0:
            myaction = random.choice(pos1)
        elif len(pos3) > 0:
            myaction = random.choice(pos3)
        elif len(pos2) > 0:
            myaction = random.choice(pos2)
        elif len(pos4) > 0:
            myaction = random.choice(pos4)

    if state.turn_type == 'Fortify':
        possible_actions = []

        for a in actions:
            if a.to_territory is not None:
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    #print("N",n,a.to_territory,a.troops)
                    if state.owners[n] != state.current_player:
                        #print("Owners",state.owners[n],state.current_player)
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

  