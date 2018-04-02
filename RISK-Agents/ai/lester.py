import randomfrom gui.aihelper import *from gui.turbohelper import *from risktools import *'''List of territories for ease of use:N. America:Alaska: NorthwestTerritories/ British Columbia/ KamchatkaNortwestTerritories: Alaska/ British Columbia/ Ontario/ GreenlandGreenland: NorthwestTerritories/ Ontario/ Iceland/ QuebecBritish Columbia: Alaska/ NorthwestTerritories/ Ontario/ Western U.S.Ontario: Greenland/ NorthwestTerritories/ British Columbia/ Western U.S./ Eastern U.S./ QuebecQuebec: Greenland/ Eastern U.S./ OntarioWestern U.S.: British Columbia/ Ontario/ Eastern U.S./ MexicoEastern U.S.: Ontario/ Western U.S./ Mexico/ QuebecMexico: Western U.S./ Eastern U.S./ ColombiaS. America:Colombia: Mexico/ Peru/ BrazilBrazil: Colombia/ Peru/ Chile/ Western AfricaPeru: Colombia/ Brazil/ ChileChile: Peru/ BrazilAfrica:South Africa: Zaire/ Ethiopia/ MadagascarZaire: Western Africa/ Ethiopia/ South AfricaEthiopia: Middle East/ Egypt/ Western Africa/ Zaire/ South Africa/ MadagascarWestern Africa: Brazil/ Zaire/ Ethiopia/ Egypt/ Western EuropeEgypt: Western Africa/ Ethiopia/ Middle East/ Southern EuropeMadagascar: Ethiopia/ South AfricaEurope:Western Europe: Western Africa/ Southern Europe/ Central Europe/ Great BritainGreat Britain: Western Europe/ Central Europe/ Sweden/ IcelandIceland: Greenland/ Great Britain/ SwedenSweden: Iceland/ Great Britain/ Central Europe/ UkraineCentral Europe: Sweden/ Great Britain/ Western Europe/ Souther Europe/ UkraineSouthern Europe: Western Europe/ Central Europe/ Ukraine/ Middle East/ EgyptUkraine: Sweden/ Central Europe/ Souther Europe/ Middle East/ Pakistan/ RussiaAsia:Middle East: Egypt/ Ethiopia/ Southern Europe/ Ukraine/ Pakistan/ IndiaPakistan: Middle East/ Ukraine/ India/ China/ RussiaRussia: Ukraine/ Pakistan/ China/ SiberiaIndia: Middle East/ Pakistan/ China/ LaosLaos: India/ China/ IndonesiaChina: Laos/ India/ Pakistan/ Siberia/ Manchuria/ RussiaManchuria: China/ Siberia/ Irkutsk/ Kamchatka/ JapanJapan: Kamchatka/ ManchuriaSiberia: China/ Manchuria/ Irkutsk/ Eastern Russia/ RussiaIrkutsk: Siberia/ Manchuria/ Kamchatka/ Eastern RussiaEastern Russia: Siberia/ Irkutsk/ KamchatkaKamchatka: Eastern Russia/ Irkutsk/ Manchuria/ Japan/ AlaskaAustralia:Indonesia: Laos/ New Guinea/ Western Australia  (INDONESIA IS THE BIG ONE THAT YOU NEED TO HOLD ON TO)New Guinea: Indonesia/ Western Australia/ Eastern AustraliaWestern Australia: Indonesia/ New Guinea/ Eastern AustraliaEastern Australia: Western Australia/ New Guinea'''#This is using Attacker AI as a template to work with.  We will be modifying it step by step following guidelines#created by Chris Wolfe#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai scriptdef getAction(state, time_left=None):    """This is the main AI function.  It should return a valid AI action for this state."""    #Get the possible actions in this state    actions = getAllowedActions(state)    #Select a Random Action    myaction = random.choice(actions)    #First thing that needs to get done is pre-assigning the territories.  This AI should target    #Indonesia first (if possible) and then go for North America and Australia evenly.  If all of both    #have been taken, go for South America, Africa, Europe, and then Asia in that order.    #RISKACTION|"PreAssign"|null|"Brazil"|null    if state.turn_type == 'PreAssign':        myPreAssignActions = getPreAssignActions(state)        for action in myPreAssignActions:            #This will guarantee that we get Indonesia if at all possible            if action.to_territory == 'Indonesia':                return action        numRemNA = 0        numRemAus = 0        for action in myPreAssignActions:            #Here we check whether or not someone already has a majority of these NA and Aus            for t in state.board.continents['N. America'].territories:                if state.board.territories[t].name == action.to_territory:                    numRemNA += 1            #Then we check if it is in Australia            for t in state.board.continents['Australia'].territories:                if state.board.territories[t].name == action.to_territory:                    numRemAus +=1        for action in myPreAssignActions:            #Here we select the first NA action if possible            for t in state.board.continents['N. America'].territories:                if state.board.territories[t].name == action.to_territory and numRemNA > numRemAus:                    return action            #Here we select the first Aus action if possible            for t in state.board.continents['Australia'].territories:                if state.board.territories[t].name == action.to_territory and numRemNA <= numRemAus:                    return action        for action in myPreAssignActions:            for t in state.board.continents['S. America'].territories:                if state.board.territories[t].name == action.to_territory:                    return action        for action in myPreAssignActions:            for t in state.board.continents['Africa'].territories:                if state.board.territories[t].name == action.to_territory:                    return action        for action in myPreAssignActions:            for t in state.board.continents['Europe'].territories:                if state.board.territories[t].name == action.to_territory:                    return action        for action in myPreAssignActions:            for t in state.board.continents['Asia'].territories:                if state.board.territories[t].name == action.to_territory:                    return action    #Now for this one, we shall preplace/place judging by the greatest power disparity, this is a formula determined    #by multiplying the number of enemy neighbors by how many total troops there are.  Whichever first one    #has the highest power disparity, gets the placement of a troop    if state.turn_type == 'PrePlace' or state.turn_type == 'Place':        if(state.turn_type == 'PrePlace'):           myPlaceActions = getPrePlaceActions(state)        else:           myPlaceActions = getPlaceActions(state)        hpd = 0        enemyTroops = 0        friendlyTroops = 0        enemyNeighbors = 0        friendlyNeighbors = 1        #Here we try to figure out what the highest power disparity is        for a in myPlaceActions:            cpd = 0            enemyTroops = 0            friendlyTroops = 0            enemyNeighbors = 0            friendlyNeighbors = 1            terrId = state.board.territory_to_id[a.to_territory]            friendlyTroops = state.armies[terrId]                        for n in state.board.territories[terrId].neighbors:                if state.owners[n] != state.current_player:                    enemyNeighbors += 1                    enemyTroops += state.armies[n]                else:                    friendlyNeighbors += 1                    friendlyTroops += state.armies[n]            cpd = (enemyNeighbors * enemyTroops) - (friendlyNeighbors * friendlyTroops)            if (cpd > hpd):                hpd = cpd        #Now we find the first spot that has that disparity and return it as an action        for a in myPlaceActions:            enemyTroops = 0            friendlyTroops = 0            enemyNeighbors = 0            friendlyNeighbors = 1            terrId = state.board.territory_to_id[a.to_territory]            friendlyTroops = state.armies[terrId]                        for n in state.board.territories[terrId].neighbors:                if state.owners[n] != state.current_player:                    enemyNeighbors += 1                    enemyTroops += state.armies[n]                else:                    friendlyNeighbors += 1                    friendlyTroops += state.armies[n]            pd = (enemyNeighbors * enemyTroops) - (friendlyNeighbors * friendlyTroops)            if (pd == hpd):                return a    if state.turn_type == 'Attack':        myAttackActions = getAttackActions(state)        myaction = actions[0]    if state.turn_type == 'Place' or state.turn_type == 'Fortify' or state.turn_type == 'PrePlace':        possible_actions = []        for a in actions:            if a.to_territory is not None:                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:                    if state.owners[n] != state.current_player:                        possible_actions.append(a)        if len(possible_actions) > 0:            myaction = random.choice(possible_actions)    return myaction#Stuff below this is just to interface with Risk.pyw GUI version#DO NOT MODIFYdef aiWrapper(function_name, occupying=None):    game_board = createRiskBoard()    game_state = createRiskState(game_board, function_name, occupying)    action = getAction(game_state)    return translateAction(game_state, action)def Assignment(player):#Need to Return the name of the chosen territory    return aiWrapper('Assignment')def Placement(player):#Need to return the name of the chosen territory     return aiWrapper('Placement')def Attack(player): #Need to return the name of the attacking territory, then the name of the defender territory    return aiWrapper('Attack')def Occupation(player,t1,t2): #Need to return the number of armies moving into new territory    occupying = [t1.name,t2.name]    aiWrapper('Occupation',occupying)def Fortification(player):    return aiWrapper('Fortification')