import random
from gui.aihelper import *
from gui.turbohelper import *
from risktools import *
from math import *

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
        
    #Select a Random Action
    myaction = random.choice(actions)
    
    if state.turn_type == 'Attack':
        maxRatio = 0
        maxRatioLoc = 0
        
        for x in actions:
            if ((x.from_territory != None) and (x.to_territory != None)):
                ratio = state.armies[state.board.territory_to_id[x.from_territory]]/state.armies[state.board.territory_to_id[x.to_territory]]
            
                if ratio > maxRatio:
                    maxRatio = ratio
                    maxRatioLoc = actions.index(x)
            
        if maxRatio >= 2:
            myaction = actions[maxRatioLoc]
        else:
            myaction = actions[len(actions)-1]
    
    if state.turn_type == 'Place' or state.turn_type == 'Fortify':
        possible_actions = []

        for a in actions:
            if a.to_territory is not None:
                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        possible_actions.append(a)
                    
        if len(possible_actions) > 0:
            myaction = random.choice(possible_actions)
    if state.turn_type=='PreAssign':
        forbidden=[]
        possible_actions=[]
        continentdic=continentvalue(state)
        filteredarray=emptycontinent(state,continentdic)
        possible_actions=action_choice(state,filteredarray,forbidden,actions)
        myaction=random.choice(possible_actions)
    return myaction

def GetTerritoryReward(state, territory):

    percentOwned = 0.0
    owned = 1
    
    if territory in state.board.continents["N. America"].territories:
        #print("N. America")
        owned += GetTerritoriesOwned(state, state.board.continents["N. America"])
        percentOwned = float((100*owned)/9)
        #print("PercentOwned:",percentOwned)
    
    elif territory in state.board.continents["S. America"].territories:
        #print("S. America")
        owned += GetTerritoriesOwned(state, state.board.continents["S. America"])
        percentOwned = float((100*owned)/4)
        #print("PercentOwned:",percentOwned)

    elif territory in state.board.continents["Europe"].territories:
        #print("Europe")
        owned += GetTerritoriesOwned(state, state.board.continents["Europe"])
        percentOwned = float((100*owned)/7)
        #print("PercentOwned:",percentOwned)

    elif territory in state.board.continents["Asia"].territories:
        #print("Asia")
        owned += GetTerritoriesOwned(state, state.board.continents["Asia"])
        percentOwned = float((100*owned)/12)
        #print("PercentOwned:",percentOwned)

    elif territory in state.board.continents["Africa"].territories:
        #print("Africa")
        owned += GetTerritoriesOwned(state, state.board.continents["Africa"])
        percentOwned = float((100*owned)/6)
        #print("PercentOwned:", percentOwned)

    elif territory in state.board.continents["Australia"].territories:
        #print("Australia")
        owned += GetTerritoriesOwned(state, state.board.continents["Australia"])
        percentOwned = float((100*owned)/4)
        #print("PercentOwned:",percentOwned)

    #print("Owned:",owned)
    #print(owned/9)
    #print(percentOwned)
    return percentOwned

def GetTerritoriesOwned(state, continent):
    Owned = 0
    for territory in continent.territories:
        #print(territory)
        if state.owners[territory] == state.current_player:
            #print("incriment")
            Owned += 1
    return float(Owned)
def getterritoriesowned(state, continent):
    Owned = 0
    for territory in continent.territories:
        #print(territory)
        if state.owners[territory] == state.current_player:
            #print("incriment")
            Owned += 1
    if Owned==0:
        Owned=float(Owned)
        Owned=.000001
    return float(Owned)
def continentvalue(state):
    valuedic={'Australia':2,'N. America':1.7,'Europe':1.25,'Asia':1.4,'Africa':1,'S. America':1}
    
    return valuedic

def emptycontinent(state, continentdic):
    for territory in state.board.continents["Australia"].territories:
        if state.owners[territory]!=state.current_player and state.owners[territory]!=None:
            continentdic['Australia']=float(continentdic['Australia']*float(getterritoriesowned(state,state.board.continents["Australia"])/4))
            #print("Aus:",float(100*GetTerritoriesOwned(state,state.board.continents["Australia"])/4)/100)
    for territory in state.board.continents["N. America"].territories:
        if state.owners[territory]!=state.current_player and state.owners[territory]!=None:
            continentdic['N. America']=float(continentdic['N. America']*float(getterritoriesowned(state,state.board.continents['N. America'])/9))
            #print("Nor:",float(GetTerritoriesOwned(state,state.board.continents['N. America'])/9))
    for territory in state.board.continents["Europe"].territories:
        if state.owners[territory]!=state.current_player and state.owners[territory]!=None:
            continentdic['Europe']=float(continentdic['Europe']*float(getterritoriesowned(state,state.board.continents['Europe'])/7))
            #print("Eur:",float(GetTerritoriesOwned(state,state.board.continents['Europe'])/7))
    for territory in state.board.continents["Asia"].territories:
        if state.owners[territory]!=state.current_player and state.owners[territory]!=None:
            continentdic['Asia']=float(continentdic['Asia']*float(getterritoriesowned(state,state.board.continents['Asia'])/12))
            #print("Asia:",float(GetTerritoriesOwned(state,state.board.continents['Asia'])/12))
    for territory in state.board.continents["Africa"].territories:
        if state.owners[territory]!=state.current_player and state.owners[territory]!=None:
            continentdic['Africa']=float(continentdic['Africa']*float(getterritoriesowned(state,state.board.continents['Africa'])/6))
            #print("Africa:",float(GetTerritoriesOwned(state,state.board.continents['Africa'])/6))
    for territory in state.board.continents["S. America"].territories:
        if state.owners[territory]!=state.current_player and state.owners[territory]!=None:
            continentdic['S. America']=float(continentdic['S. America']*float(getterritoriesowned(state,state.board.continents['S. America'])/4))
            #print("Sou:",float(GetTerritoriesOwned(state,state.board.continents['S. America'])/4))
    
    return continentdic
def getContinents(state):
    australia=state.board.continents["Australia"]
    Asia=state.board.continents["Asia"]
    Africa=state.board.continents["Africa"]
    Europe=state.board.continents["Europe"]
    NAmerica=state.board.continents["N. America"]
    SAmerica=state.board.continents["S. America"]
    continents=[australia,Asia,Africa,Europe,NAmerica,SAmerica]
def highestvalue(state,filteredarray,forbidden):
    highest=0
    highestc=""
    if filteredarray['Australia']>highest and 'Australia' not in forbidden:
            highest=filteredarray['Australia']
            highestc="Australia"
    if filteredarray['N. America']>highest and 'N. America' not in forbidden:
            highest=filteredarray['N. America']
            highestc="N. America"
    if filteredarray['S. America']>highest and 'S. America' not in forbidden:
            highest=filteredarray['S. America']
            highestc="S. America"
    if filteredarray['Africa']>highest and 'Africa' not in forbidden:
            highest=filteredarray['Africa']
            highestc="Africa"
    if filteredarray['Europe']>highest and 'Europe' not in forbidden:
            highest=filteredarray['Europe']
            highestc="Europe"
    if filteredarray['Asia']>highest and  'Asia' not in forbidden:
            highest=filteredarray['Asia']
            highestc="Asia"
    #print(filteredarray['Australia'])
    #print(filteredarray['N. America'])
    #print(filteredarray['S. America'])
    #print(filteredarray['Africa'])
    #print(filteredarray['Africa'])
    #print(filteredarray['Europe'])
    #print(filteredarray['Asia'])
    return highestc
def action_choice(state,filteredarray,forbidden,actions):
    highestc=highestvalue(state,filteredarray,forbidden)
    possible_actions=[]
    for a in actions:
            if a.to_territory is not None:
                for territories in state.board.continents[highestc].territories:
                    if territories==state.board.territory_to_id[a.to_territory]:
                        possible_actions.append(a)
    if len(possible_actions)<1:
        #for x in forbidden:
            #print("constant")
            #print(x)
        forbidden.append(highestc)
        possible_action=action_choice(state,filteredarray,forbidden,actions)
        return possible_action
    else:
        return possible_actions
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

  
