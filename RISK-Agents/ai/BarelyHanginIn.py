import random
import numpy
from risktools import *



#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    global AI_ID, OTHER
    AI_ID = state.current_player
    if AI_ID == 0:
        OTHER = 1
    else:
        OTHER = 0


    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    if state.turn_type == 'PreAssign':
        to_terr = Assignment(state)
        if type(to_terr) is int:
            temp = to_terr
            to_terr = state.board.territories[to_terr].name
        a = RiskAction('PreAssign', to_terr, None, None)
        return a
    elif state.turn_type == 'PrePlace':
        to_terr = Placement(state)
        b = RiskAction('PrePlace', to_terr, None, None)
        return b
    elif state.turn_type == 'Place':
        to_terr = Placement(state)        
        c = RiskAction('Place', to_terr, None, None)
        return c
    elif state.turn_type == 'TurnInCards':
        return random.choice(actions)
    elif state.turn_type == 'Attack':
        ai_terr, enemy_terr = Attack(state)
        if ai_terr == None:
            nextPlayer(state)
        e = RiskAction('Attack', ai_terr, enemy_terr, None)
        return e
    elif state.turn_type == 'Occupy':
        ammt = Occupation(state, state.last_defender, state.last_attacker)
        d = state.board.territories[state.last_defender].name
        a = state.board.territories[state.last_attacker].name
        f = RiskAction('Occupy', d, a, ammt)
        return f
    elif state.turn_type == 'Fortify':
        g = Fortification(state)
        return g

def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    action = getAction(game_state)
    return translateAction(game_state, action)

    
def isFront(state, t):
    pid = state.owners[t]
    for n in state.board.territories[t].neighbors:
        if state.owners[n] != pid:
            return True
    return False 

def GetMyTerr(state):
    myplaces = []
    n = 0
    while n < len(state.owners):
        if state.owners[n] == AI_ID:
            myplaces.append(n)
        n = n + 1
    return myplaces
  
def GetMyFront(state):
    #Helper function, with output list of front territories of the AI.
    #owners an array that is 42 long each has a player number so if player number matches that is your terr
    #state.board.territories an array of reick terr ob (same terr id as in state array). Terrid 5 matches my owner, state.armies[5] is my marmies int that terr
    #state.board.territories[n].neighbors will give you an array of a terr's neighbors.
    myfront = []
    n = 0
    while n < 42:
        if state.owners[n] == AI_ID:
            if isFront(state, n):
                myfront.append(n)
        n = n + 1
    return myfront
    


def GetTerrOrderedByArmy(state, consideration):
    #helper function should ACCEPT THE RETURN VALUE FROM GetMyFront
    #(but it can accept any list of territories)
    #This will return a list of all of the AI's front territories
    #which have an armies size greater than 1. Also, the returned list
    #is made of terr objects ordered from largest army to smallest army. 
    
    #alist constain the size of the armies for each territory in consideration.
    #The native order of considersation is retained in alist.
    alist = []
    #List of territories for the new consideration. These territories are
    #have armies not equl to 1. 
    newCon = []
    n = 0
    
    while n < len(consideration):
        if state.armies[consideration[n]] == 1:
            n = n + 1
        else:
            newCon.append(consideration[n])
            alist.append(state.armies[consideration[n]])
            n = n + 1
            
    if len(newCon) == 0:
        if len(consideration) == 0:
            return consideration
        out = []
        out.append(consideration[0])
        return out

    if len(newCon) == 1:
        return newCon
    
    #now we have a list of armies (alist) and a list of AI's terrs (newCon)
    #ordered by the same index as each other
    
    alist.sort(reverse=True)
    n = 0
    output = []
    while n < len(alist):
        m = 0
        while m < len(newCon):
            if alist[n] == state.armies[newCon[m]]:
                output.append(newCon[m])
            m = m + 1
        n = n + 1
    return(newCon)
                                            


def MostEnemyTerr(state):
    #Helper function, counts the number of enemy neighbors each territory the
    #AI owns, and orders those territories from most enemy neighbors to least
    #enemy neighbors.

    #myplaces is a list of all of the AI's territories
    myplaces = GetMyFront(state)

    #enemyNeighCnt is a list that has the number of enemy territories neighbor
    #each of the AI's territories. 
    enemyNeighCnt = []
    i = 0
    while i < len(myplaces):
        temp = 0
        for each in state.board.territories[myplaces[i]].neighbors:  #LOOOOK THIS IS HOW YOU FIND TERR NEIGHS
            if state.owners[each] == AI_ID:  #if state.owners[each] == AI_ID then temp = temp +1
                temp = temp + 1
        enemyNeighCnt.append(temp)
        i = i + 1

    #mostEnemies is the eventual output of the function. This list contains the
    #ordered list of the territories that will be returned based on number of
    #neighboring enemy territories. 
    mostEnemies = []
    maxE = max(enemyNeighCnt)
    maxI = []
    n = 0
    for each in enemyNeighCnt:
        if each == maxE:
            maxI.append(n)
            break
        else:
            n = n + 1
    for each in maxI:
        mostEnemies.append(myplaces[each])

    return mostEnemies


def TerrIsMine(state, t):
    if state.owners[t] == AI_ID:
        return True
    else:
        return False
    
def TerrOwner(state, t):
    if state.owners[t] == None:
        return None
    elif state.owners[t] == AI_ID:
        return True
    else:
        return False

def TerrWeakestFront(state, t):
    weakestOpt = []
    for each in state.board.territories[t].neighbors:
        if state.owner[each] != AI_ID:
            weakestOpt.append(state.board.territories[each])

    minA = 1000
    output = None
    for each in weakestOpt:
        if each.armies < minA:
            minA = each.armies
            output = each
    return output



def TerrPressure(state, t):
    pressure = 0
    neigh = GetNeighbors(state, t)
    for each in neigh:
        if state.owners[each] == OTHER or state.owners[each] == None or state.owners[each] != AI_ID:
            pressure = pressure + 1
            
    return pressure
            

def GetTerritory(state, t):
    if type(t) is int:
        return t
    else:
        return state.board.territory_to_id[t]

def GetNeighbors(state, t):
    if type(t) is int:
        return state.board.territories[t].neighbors
    else:
        return state.board.territories[GetTerritory(state, t)].neighbors


            
def Assignment(state):
    #Need to Return the name of the chosen territory
    #First case: Very beginning of the, just select a random country, and name
    #this country "original"


    b = getAllowedActions(state)
    if len(b) > 40:
        c = random.choice(b)
        return c.to_territory

    open_terr = []
    for each in b:
        a = each.to_territory
        open_terr.append(GetTerritory(state, a))

    if len(open_terr) == 1:
        return open_terr[0]

    
    best = []
    n = 0
    while n < len(open_terr):
        a = GetNeighbors(state, open_terr[n])
        b = 0
        for each in a:
            if state.owners[each] == AI_ID:
                b = b + 1
        best.append(b)
        n = n + 1
    maxB = max(best)
    n = 0
    to_terr = None
    while n < len(best):
        if best[n] == maxB:
            to_terr = open_terr[n]
        n = n + 1

    return state.board.territories[to_terr].name
            
                

     
def Placement(state):
    #Will try add to the front territory which has the most soldiers already.
    #If all the front territories have 1 army each, it will instead add to
    #the AI's territory with the most neighboring enemy territories. 
    
    firstPlace = GetMyFront(state)
    test = True
    for each in firstPlace:
        if state.armies[each] != 1:
            test = False

    if test == True:
        terrPress = []
        for each in firstPlace:
            terrPress.append(TerrPressure(state, each))
        try:
            maxP = max(terrPress)
            n = 0
            while n < len(terrPress):
                if terrPress[n] == maxP:
                    return state.board.territories[firstPlace[n]].name
                n = n + 1
        except ValueError:
            b = getAllowedActions(state)
            a = random.choice(b)
            c = a.to_territory
            return state.board.territories[GetTerritory(state,c)].name
            

    options = GetTerrOrderedByArmy(state, GetMyFront(state))
    

    if len(options) == 1:
        return state.board.territories[options[0]].name
    else:
        terrArmies = []
        for each in options:
            terrArmies.append(state.armies[each])
        maxA = max(terrArmies)
        n = 0
        while n < len(terrArmies):
            if terrArmies[n] == maxA:
                return state.board.territories[options[n]].name
            n = n + 1


    
def Attack(state):
    #At this point, Attack just uses the AI's front territory with the largest
    #army, and attack's its neighbor which is has the smallest army. 

    #options is an ordered list (high to low) based on armies size of front
    #territories
    options = GetTerrOrderedByArmy(state, GetMyFront(state))
    if len(options) == 0:
        options = GetMyFront(state)
    
    neigh = GetNeighbors(state, options[0])
    the_neigh = []
    for each in neigh:
        if state.owners[each] != AI_ID:
            the_neigh.append(each)
    alist = []
    n = 0
    while n < len(the_neigh):
        alist.append(state.armies[the_neigh[n]])
        n = n + 1
    minA = min(alist)
    n = 0
    output = []
    while n < len(alist):
        if alist[n] == minA:
            output.append(the_neigh[n])
        n = n + 1
    
    if state.armies[options[0]] == 1:
        return None, None
    
    return state.board.territories[output[0]].name, state.board.territories[options[0]].name
        

   
def Occupation(state,t1,t2):
    #At the end of the attack, we need to move our armies to the new territory.
    #This function determines how many soldiers go where. Could be altered to be
    #better, or we could alter and see how bad things get if we change this
    #and discuss that in the write up.

    a = getAllowedActions(state)
    maxAmt = 0
    minAmt = 0
    amt = []
    for each in a:
        amt.append(each.troops)
    maxA = max(amt)
    minA = min(amt)

    if isFront(state, t1) is False:
        return minA
    else:
        if maxA > 20:
            blah = [0,1,1,2]
            sub = random.choice(blah)
            out = maxA-sub
            return out
        elif maxA > 10:
            blah = [0,1,2]
            sub = random.choice(blah)
            out = maxA-sub
            return out 
        else:
            return maxA

        
                    


def Fortification(state):
    a = (getFortifyActions(state))
    if len(a) == 0:
        out = RiskAction('Fortify', None, None, 0)
        return out
    
        
    to = []
    frm = []
    amt = []
    maxAmt = 0
    minAmt = 0
    for each in a:
        terr = each.from_territory
        try:
            terr = state.board.territory_to_id[terr]
            hold = isFront(state, terr)
            if hold == False:
                amt.append(each.troops)
                to.append(each.to_territory)
                frm.append(each.from_territory)
        except KeyError:
            continue
    try:
        maxA = max(amt)
    except ValueError:
        out = RiskAction('Fortify', None, None, 0)
        return out
    
    if maxA  < 4:
        out = RiskAction('Fortify', None, None, 0)
        return out

    
    n = 0
    save = 0
    while n < len(amt):
        if amt[n] == maxA:
            save = n
        n = n + 1
    frm_fin = frm[save]
    to_fin = to[save]

    nb = GetNeighbors(state, frm[save])
    for each in nb:
        if isFront(state, each):
            if TerrIsMine(state, each):
                to_fin = state.board.territories[each].name
            

    out = RiskAction('Fortify', to_fin, frm_fin, maxA)
    return out

