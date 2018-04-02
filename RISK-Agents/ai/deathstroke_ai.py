import riskengine
import riskgui
import random
import time
from aihelper import *
from turbohelper import *
from risktools import *
from array import *
from copy import *

#PA3_RISK assignment for Peter Opel, Luke Smith, and Adam Griffin

priorityCountries = ["Colombia", "Brazil", "Peru", "Chile", "Mexico", "Western U.S.", "Eastern U.S.", "British Columbia", "Alaska", "Quebec", "Greenland", "Ontario", "NorthwestTerritories", "Western Africa", "Egypt", "Ethiopia", "Zaire", "Madagascar", "South Africa", "Kamchatka","Iceland", "Great Britain", "Sweden", "Western Europe", "Southern Europe", "Central Europe", "Ukraine", "Middle East", "Pakistan","India", "Russia", "Siberia", "Eastern Russia", "Irkutsk", "Manchuria", "Japan", "China", "Laos", "Indonesia", "New Guinea", "Western Australia", "Eastern Australia"]
probablityTable = {1:{
    1: .42,
    2: .75,
    3: .92,
    4: .97,
    5: .99,
    6: 1,
    7: 1,
    8: 1,
    9: 1,
    10: 1,
    11: 1,
    12: 1,
    13: 1,
    14: 1,
    15: 1,
    16: 1,
    17: 1,
    18: 1,
    19: 1,
    20: 1}, 2:{
        1: .11,
        2: .36,
        3: .66,
        4: .79,
        5: .89,
        6: .93,
        7: .97,
        8: .98,
        9: .99,
        10: .99,
        11: .99,
        12: .99,
        13: 1,
        14: 1,
        15: 1,
        16: 1,
        17: 1,
        18: 1,
        19: 1,
        20: 1},3:{
            1: .03,
            2: .21,
            3: .47,
            4: .64,
            5: .77,
            6: .86,
            7: .91,
            8: .95,
            9: .97,
            10: .98,
            11: .99,
            12: .99,
            13: .99,
            14: .99,
            15: .99,
            16: .99,
            17: .99,
            18: .99,
            19: .99,
            20: .99},4:{
                1: .01,
                2: .09,
                3: .31,
                4: .48,
                5: .64,
                6: .74,
                7: .83,
                8: .89,
                9: .93,
                10: .95,
                11: .97,
                12: .98,
                13: .99,
                14: .99,
                15: .99,
                16: .99,
                17: .99,
                18: .99,
                19: .99,
                20: .99},5:{
                    1: .005,
                    2: .05,
                    3: .21,
                    4: .36,
                    5: .51,
                    6: .64,
                    7: .74,
                    8: .82,
                    9: .87,
                    10: .92,
                    11: .97,
                    12: .98,
                    13: .99,
                    14: .99,
                    15: .99,
                    16: .99,
                    17: .99,
                    18: .99,
                    19: .99,
                    20: .99},6:{
                        1: .005,
                        2: .02,
                        3: .13,
                        4: .25,
                        5: .4,
                        6: .52,
                        7: .64,
                        8: .73,
                        9: .81,
                        10: .86,
                        11: .94,
                        12: .96,
                        13: .98,
                        14: .99,
                        15: .99,
                        16: .99,
                        17: .99,
                        18: .99,
                        19: .99,
                        20: .99},7:{
                            1: 0,
                            2: .01,
                            3: .08,
                            4: .18,
                            5: .30,
                            6: .42,
                            7: .54,
                            8: .64,
                            9: .73,
                            10: .8,
                            11: .85,
                            12: .89,
                            13: .93,
                            14: .95,
                            15: .96,
                            16: .98,
                            17: .99,
                            18: .99,
                            19: .99,
                            20: .99},8:{
                                1: .05,
                                2: .05,
                                3: .05,
                                4: .12,
                                5: .22,
                                6: .33,
                                7: .45,
                                8: .55,
                                9: .65,
                                10: .72,
                                11: .79,
                                12: .84,
                                13: .89,
                                14: .92,
                                15: .94,
                                16: .95,
                                17: .97,
                                18: .98,
                                19: .99,
                                20: .99},9:{
                                    1:0,
                                    2: .005,
                                    3: .03,
                                    4: .09,
                                    5: .16,
                                    6: .26,
                                    7: .36,
                                    8: .46,
                                    9: .56,
                                    10: .65,
                                    11: .72,
                                    12: .79,
                                    13: .84,
                                    14: .88,
                                    15: .91,
                                    16: .94,
                                    17: .95,
                                    18: .97,
                                    19: .98,
                                    20: .98},10:{
                                        1:0,
                                        2:0,
                                        3: .02,
                                        4: .06,
                                        5: .12,
                                        6: .19,
                                        7: .29,
                                        8: .38,
                                        9: .48,
                                        10: .57,
                                        11: .65,
                                        12: .72,
                                        13: .79,
                                        14: .83,
                                        15: .88,
                                        16: .91,
                                        17: .93,
                                        18: .95,
                                        19: .97,
                                        20: .97},11:{
                                            1:0,
                                            2:0,
                                            3:.01,
                                            4:.03,
                                            5:.09,
                                            6:.14,
                                            7:.22,
                                            8:.31,
                                            9:.40,
                                            10:.49,
                                            11:.58,
                                            12:.66,
                                            13:.72,
                                            14:.78,
                                            15:.83,
                                            16:.87,
                                            17:.90,
                                            18:.92,
                                            19:.94,
                                            20:.96},12:{
                                                1:0,
                                                2:0,
                                                3:0,
                                                4:.03,
                                                5:.06,
                                                6:.11,
                                                7:.17,
                                                8:.24,
                                                9:.33,
                                                10:.42,
                                                11:.51,
                                                12:.58,
                                                13:.66,
                                                14:.72,
                                                15:.78,
                                                16:.82,
                                                17:.86,
                                                18:.89,
                                                19:.92,
                                                20:.94},13:{
                                                    1:0,
                                                    2:0,
                                                    3:0,
                                                    4:.02,
                                                    5:.04,
                                                    6:.08,
                                                    7:.13,
                                                    8:.19,
                                                    9:.26,
                                                    10:.35,
                                                    11:.43,
                                                    12:.52,
                                                    13:.59,
                                                    14:.67,
                                                    15:.73,
                                                    16:.78,
                                                    17:.83,
                                                    18:.86,
                                                    19:.89,
                                                    20:.92},14:{
                                                        1:0,
                                                        2:0,
                                                        3:0,
                                                        4:.01,
                                                        5:.03,
                                                        6:.06,
                                                        7:.10,
                                                        8:.15,
                                                        9:.22,
                                                        10:.29,
                                                        11:.37,
                                                        12:.45,
                                                        13:.53,
                                                        14:.60,
                                                        15:.67,
                                                        16:.73,
                                                        17:.78,
                                                        18:.82,
                                                        19:.86,
                                                        20:.89},15:{
                                                            1:0,
                                                            2:0,
                                                            3:0,
                                                            4:0,
                                                            5:.02,
                                                            6:.04,
                                                            7:.07,
                                                            8:.12,
                                                            9:.17,
                                                            10:.24,
                                                            11:.31,
                                                            12:.39,
                                                            13:.46,
                                                            14:.54,
                                                            15:.61,
                                                            16:.67,
                                                            17:.73,
                                                            18:.78,
                                                            19:.82,
                                                            20:.86}, 16:{
                                                                1:0,
                                                                2:0,
                                                                3:0,
                                                                4:0,
                                                                5:.01,
                                                                6:.03,
                                                                7:.05,
                                                                8:.08,
                                                                9:.13,
                                                                10:.19,
                                                                11:.26,
                                                                12:.33,
                                                                13:.40,
                                                                14:.47,
                                                                15:.55,
                                                                16:.61,
                                                                17:.68,
                                                                18:.73,
                                                                19:.78,
                                                                20:.82},17:{
                                                                    1:0,
                                                                    2:0,
                                                                    3:0,
                                                                    4:0,
                                                                    5:0,
                                                                    6:.02,
                                                                    7:.04,
                                                                    8:.07,
                                                                    9:.11,
                                                                    10:.15,
                                                                    11:.21,
                                                                    12:.28,
                                                                    13:.34,
                                                                    14:.42,
                                                                    15:.48,
                                                                    16:.56,
                                                                    17:.62,
                                                                    18:.68,
                                                                    19:.73,
                                                                    20:.78},18:{
                                                                        1:0,
                                                                        2:0,
                                                                        3:0,
                                                                        4:0,
                                                                        5:0,
                                                                        6:.01,
                                                                        7:.03,
                                                                        8:.05,
                                                                        9:.08,
                                                                        10:.12,
                                                                        11:.17,
                                                                        12:.23,
                                                                        13:.29,
                                                                        14:.36,
                                                                        15:.43,
                                                                        16:.49,
                                                                        17:.56,
                                                                        18:.62,
                                                                        19:.68,
                                                                        20:.73},19:{
                                                                            1:0,
                                                                            2:0,
                                                                            3:0,
                                                                            4:0,
                                                                            5:0,
                                                                            6:.01,
                                                                            7:.02,
                                                                            8:.03,
                                                                            9:.06,
                                                                            10:.09,
                                                                            11:.13,
                                                                            12:.18,
                                                                            13:.24,
                                                                            14:.31,
                                                                            15:.37,
                                                                            16:.44,
                                                                            17:.50,
                                                                            18:.57,
                                                                            19:.63,
                                                                            20:.68},20:{
                                                                                1:0,
                                                                                2:0,
                                                                                3:0,
                                                                                4:0,
                                                                                5:0,
                                                                                6:0,
                                                                                7:.01,
                                                                                8:.03,
                                                                                9:.05,
                                                                                10:.07,
                                                                                11:.11,
                                                                                12:.15,
                                                                                13:.20,
                                                                                14:.26,
                                                                                15:.32,
                                                                                16:.38,
                                                                                17:.45,
                                                                                18:.51,
                                                                                19:.58,
                                                                                20:.63}
                   }
def getChances(state, attacking, defending):
    if((attacking <= 20) and (defending <= 20)):
        return probablityTable[int(defending)][int(attacking)]
    elif(((attacking > 20) and (defending > 10)) or ((defending > 20) and (attacking > 10))):
        newAttack = attacking - 10
        newDefend = defending - 10
        return getChances(state, newAttack, newDefend)
    else:
        if(defending < attacking):
            return 1
        else:
            return 0
        
def continentAttackable(state, continentObject):
    for terr in continentObject.territories:
        for each in state.board.territories[terr].neighbors:
            if(territoryOwned(state, each)):
                return True
    return False

def getFocusedCont(state):
    bestCont = None
    mostFocusRatio = -1.0

    if(continentOwned(state, state.board.continents['S. America']) == False):
        return state.board.continents['S. America'] 
    #Find focus contients
    ratios = {}
    for i in state.board.continents:
        continent = state.board.continents[i]

        ownedTerritory = 0.0
        totalTerritory = 0.0
        for each in continent.territories:
            if(territoryOwned(state, each)):
                ownedTerritory += 1
            totalTerritory +=1

        ratio = ownedTerritory / totalTerritory
        ratios[continent.name] = ratio
        if ((ratio > mostFocusRatio) and (ratio != 1.0) and continentAttackable(state, continent)):
            mostFocusRatio = ratio
            bestCont = continent
    
    if((continentOwned(state, state.board.continents['N. America']) == False) and (continentOwned(state, state.board.continents['Africa']) == False)):
        if(ratios['N. America'] >= ratios['Africa']):
            return state.board.continents['N. America']
        else:
            return state.board.continents['Africa']
    elif(continentOwned(state, state.board.continents['N. America']) == False):
        return state.board.continents['N. America']
    elif(continentOwned(state, state.board.continents['Africa']) == False):
        return state.board.continents['Africa']
    else:
        return bestCont
       
def getBeginTurnPlace(state):
    
    focused = getFocusedCont(state)
    highestAlly = None
    highestAllyCount = 0
    bestPick = None
    highestDiff = -15
    lowestTroopCount = 100000
    borders = getBorders(state)

    owned = getOwnedTerrs(state)
    
    if(focused != None):
        for terr in focused.territories:
            if(territoryOwned(state, terr) == False):
                for neigh in state.board.territories[terr].neighbors:
                    if(territoryOwned(state, neigh)):
                        if(state.armies[neigh] > highestAllyCount):
                            highestAlly = neigh
                            highestAllyCount = state.armies[neigh]
                        if(getChances(state, state.armies[highestAlly], state.armies[terr]) <= .75):
                            bestPick = highestAlly
    if(bestPick == None):
        for each in borders:
            diff = getTroopDifference(state, each)
            if(diff > highestDiff):
                bestPick = each
                highestDiff = diff
    if(bestPick == None):
        owned = getOwnedTerrs(state)
        for terr in owned:
            if(state.armies[terr] < lowestTroopCount):
                bestPick = terr
                lowestTroopCount = state.armies[terr]

    return state.board.territories[bestPick].name
    #return state.board.territories[vulnerable].name
   
def troopsToTakeCountry(state, enemy):
    ally = None
    highest = 0
    for each in state.board.territories[enemy].neighbors:
        if(territoryOwned(state, each)):
            if(state.armies[each] > highest):
                ally = each
                highest = state.armies[each]
    if(ally == None):
        return False
    
    allyTroops = state.armies[ally]
    enemyTroops = state.armies[enemy]
    while(getChances(state, allyTroops, enemyTroops) < .7):
        allyTroops += 1
    return [allyTroops, ally]

    
#fortifies the owned borders.
def fortifyOwnedContinents(state):
    country = False

    borders = getBorders(state)
    ownedBorders = getOwnedBorders(state, borders)
    greatestDiff = 0
    for each in ownedBorders:
        diff = getTroopDifference(state, each)
        if (diff > greatestDiff):
            greatestDiff = diff
            country = each

    return country

#Get State Neighbors
def getTroopNeighborArray(state, allyTerrID):
    stateNeighbors = []
    for each in state.board.territories[allyTerrID].neighbors:
        stateNeighbors.append(each)
    return stateNeighbors


#Function to get avaiable priority country name
def checkThroughPriorityCountries(state):
    for j in range(len(priorityCountries)):
        if j < 20:
            for i in range(len(state.owners)):
                if state.owners[i] is None:
                    to_territory = state.board.territories[i].name
                    if to_territory == priorityCountries[j]:
                        '''
                        riskgui.set_status(priorityCountries[j])
                        numAllies = countBorderingAllies(state, state.board.territories[i])
                        riskgui.set_status(str(numAllies))
                        '''
                        return priorityCountries[j]
                        #return RiskAction('PreAssign', priorityCountries[j], None, None)
        else:
            return getClosestPick(state)
def cout(string):
    a = True
    #riskgui.set_status(string)

def territoryOwned(state, territoryID):
    if(state.owners[territoryID] == state.current_player):
        return True
    else:
        return False

def getOwnedTerrs(state):
    owned = []
    for each in state.board.territories:
        if(territoryOwned(state, each.id)):
           owned.append(each.id)
    return owned
    
def shortestPathToAlly(state, country):
    global minDist
    global bestPath
    minDist = 50
    currentPath = []
    currentPath.append(country)
    bestPath = []
    shortestPath = DFS(state, currentPath)
    return shortestPath

def DFS(state, currentPath):
    global minDist
    global bestPath
    neighbors = currentPath[len(currentPath)-1].neighbors
    for each in neighbors:
        neigh = state.board.territories[each]
        if(neigh not in currentPath):
            #we want the new current path to only have the current neighbor appended
            newCP = deepcopy(currentPath)
            newCP.append(neigh)
            
            if(territoryOwned(state, neigh.id)):
                length = len(newCP)
                if(length < minDist):
                    minDist = length
                    bestPath = newCP
                elif(length == minDist):
                    prevAlly = bestPath[len(bestPath)-1]
                    if(priorityCountries.index(neigh.name) < priorityCountries.index(prevAlly.name)):
                        minDist = length
                        bestPath = newCP
                return bestPath
            elif(len(newCP) <= minDist):
                bestPath = DFS(state, newCP)
            else:
                return bestPath
    return bestPath
                
def getClosestPick(state):
    allies = 0
    bestPick = False
    bestDist = 30
    for i in range(20, len(priorityCountries)):
        for j in range(len(state.owners)):
            if(state.owners[j] == None):
                if(state.board.territories[j].name == priorityCountries[i]):
                    tempAllies = countBorderingAllies(state, state.board.territories[j])
                    if(tempAllies > allies):
                        allies = tempAllies
                        bestPick = priorityCountries[i]
    
    if(allies > 0):
        return bestPick
    else:
        for i in range(20, len(priorityCountries)):
            for j in range(len(state.owners)):
                if(state.owners[j] == None):
                    if(state.board.territories[j].name == priorityCountries[i]):
                        shortestPath = shortestPathToAlly(state, state.board.territories[j])
                        
                        if (len(shortestPath) < bestDist):
                            bestDist = len(shortestPath)
                            bestPick = priorityCountries[i]
                            bestPath = shortestPath
        
        return bestPick

def countBorderingAllies(state, country):
    count = 0
    for i in range(len(country.neighbors)):
        neighborID = country.neighbors[i]
        if(state.owners[neighborID] == state.current_player):
            count += 1
    return count

#Start of PrePlace code
def fortify(state):
    borders = getBorders(state)
    ownedBorders = getOwnedBorders(state, borders)

    
    pick = None
    pickFound = False
    ownedDifference = -1
    difference = -1000
    #Select default pick if all borders are satisfactory
   # for each in priorityCountries:
    #    for terr in ownedBorders:
     #       if (state.board.territories[terr].name == each) and (pick == None):
      #          pick = terr
       
    for border in ownedBorders:
        diff = getTroopDifference(state, border)
        if diff > ownedDifference:
            pickFound = True
            pick = border
            ownedDifference = diff
        elif ((diff == ownedDifference) and (diff != -1)) and (priorityCountries.index(state.board.territories[border].name) < (priorityCountries.index(state.board.territories[pick].name))):
            pickFound = True
            pick = border
            ownedDifference = diff
    if(pickFound == False):
        for border in borders:
            diff = getTroopDifference(state, border)
            if diff > difference:
                pick = border
                difference = diff
            elif ((diff == difference) and (diff != 0)) and (priorityCountries.index(state.board.territories[border].name) < (priorityCountries.index(state.board.territories[pick].name))):
                pick = border
                difference = diff
   
            
    return state.board.territories[pick].name

def getTroopDifference(state, allyTerrID):
    allyTroops = state.armies[allyTerrID]

    highestID = None
    highestCount = 0
    for each in state.board.territories[allyTerrID].neighbors:
        if(territoryOwned(state, each) == False):
            enemyCount = state.armies[each]
            if(enemyCount > highestCount):
                highestID = each
                highestCount = enemyCount
                
    if(highestID != None):
        enemyTroops = state.armies[highestID]
        return(enemyTroops - allyTroops)
    else:
        return 0
    

def getOwnedBorders(state, borders):
    ownedBorders = []
    for key in state.board.continents:
        continent = state.board.continents[key]
        if(continentOwned(state, continent)):
            for terr in continent.territories:
                for neigh in state.board.territories[terr].neighbors:
                    if(territoryOwned(state, neigh) == False):
                        if terr not in ownedBorders:
                            ownedBorders.append(terr)

    return ownedBorders

def continentOwned(state, continentObject):
    owned = True
    for terr in continentObject.territories:
        if(territoryOwned(state, terr) == False):
            owned = False
    return owned
           
def getBorders(state):
    borders = []
    owned = getOwnedTerrs(state)
    for i in owned:
        neighbors = state.board.territories[i].neighbors
        for neigh in neighbors:
            if(territoryOwned(state, neigh) == False):
                if i not in borders:
                    borders.append(i)
    return borders
    
def sameContinent(state, terrID1, terrID2):
    for key in state.board.continents:
        continent = state.board.continents[key]
        for terr in continent.territories:
            if terr == terrID1:
                continent1 = continent
            if terr == terrID2:
                continent2 = continent
    if(continent1 == continent2):
        return True
    else:
        return False
def keepAttacking(state):
    focused = getFocusedCont(state)
    if(state.last_defender == None):
        return True
    if(state.last_defender in focused.territories):
        return True
    else:
        return False

def attackPlan(state):
    #returns information as an array [defending country, attacking country]

    enemyChoice = None
    allyChoice = None

    borders = getBorders(state)
    for terr in borders:
        for neigh in state.board.territories[terr].neighbors:
            if(territoryOwned(state, neigh) == False):
                if(getChances(state, state.armies[terr], state.armies[neigh]) > .75):
                    enemyChoice = neigh
                    allyChoice = terr
    
                
    if((enemyChoice != None) and (allyChoice != None)):
        enemyID = state.board.territories[enemyChoice].name
        allyID = state.board.territories[allyChoice].name
        result = [enemyID, allyID]
        #result = [enemyChoice, allyChoice]
        return result
    else:
        return [None, None]

def attackable(state, terrID):
    for neigh in state.board.territories[terrID].neighbors:
        if territoryOwned(state, neigh):
            return True
        
    return False
        

def occupyPlan(state):
    #retun [to territory, from territory, moving troop count]
    fromCountry = state.last_attacker
    toCountry = state.last_defender
    troopCount = state.armies[fromCountry]
    move = 0
    if(troopCount >= 6):
       
        move = math.ceil(troopCount / 2)
        move = int(move)
    elif(troopCount == 5) or (troopCount == 4):
        move = 3
    else:
        move = troopCount - 1
    
    result = [state.board.territories[toCountry].name, state.board.territories[fromCountry].name, move]
    return result

def fortifyPlan(state):
    
    return [None, None, None]
#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    cout(str("type: "+ state.turn_type))
    
    """This is the main AI function.  It should return a valid AI action for this state."""
    if state.turn_type == 'PreAssign': #Check to see if turn type is Pre-Assign
        return RiskAction('PreAssign', checkThroughPriorityCountries(state), None, None)
    if state.turn_type == 'PrePlace':
        return RiskAction('PrePlace', fortify(state), None, None)
    if state.turn_type == 'Place':
        
        return RiskAction('Place', getBeginTurnPlace(state), None, None)
    if state.turn_type == 'Attack':
        result = attackPlan(state)
        return RiskAction('Attack', result[0], result[1], None)
        
    if state.turn_type == 'Occupy':
        result = occupyPlan(state)
        
        return RiskAction('Occupy', result[0], result[1], result[2])
    if state.turn_type == 'Fortify':
        result = fortifyPlan(state)
        return RiskAction('Fortify', result[0], result[1], result[2])
    if state.turn_type == 'TurnInCards':
        return getTurnInCardsActions(state)[0]
        
        
    
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

  
