import gui.riskengine
import gui.riskgui
import random
from gui.aihelper import *
from gui.turbohelper import *
from risktools import *

import math

#Artificial Intelligence (RISK:ClashoftheAIs)
#Code by Roger Garcia, Delma Nieves, Beck , Fall 2016
#rsg169@msstate.edu
#din7@msstate.edu
#pjb82@msstate.edu
#

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""

    #print state info 
    #print_state_info(state,False)

    #Get info on Agent
    name = state.players[state.current_player].name
    player_id = state.players[state.current_player].id
    turn_type = state.turn_type
    free_armies = state.players[state.current_player].free_armies
    cards = state.players[state.current_player].cards
    conquered_territory = state.players[state.current_player].conquered_territory

    
    #Get array of RiskCard objects (cards) 
    board_cards = list(state.board.cards)

    # higher value more susceptible if we pick this action
    # susceptible_pick = number of enemies territories surrounding this pick 
    # cuttoff for number of enemies territories surrounding this pick
    lower_bound = 3 # 3 and 6 
    upper_bound = 6 
    
    percent_armies = 0.60

    #Get the possible actions in this state
    actions = getAllowedActions(state)
    

    #Create a Rank Lookup-Table based on priority list(For PreAssign)
    # prefer = [10,9,38, \
    #             24,8,0,2, \
    #             11,12,38,39,40,41, \
    #             6,7,5,4,3,1, \
    #             21,19,23,24,25,20,22, \
    #             26,37,30,17,16,15, \
    #             13,14,18,27,28,29,31,32,33,34,35,36]

    # S.A, Australia, Europe, North America, Africa, Asia.
    prefer = [9,11,12,10, \
    41,40,38,39, \
    20, 21, 22, 19, 23, 24, 25,\
    0, 1, 3, 6, 8, 7, 4, 5, 2, \
    16, 14, 13, 15, 17, 18, \
    26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]

    #change of prefer list increases our winnning percentage. 400 games. Attacker 64+-5 ClashAI: 336 +-5
    # prefer = range(0,42)
    # prefer.reverse()


    # dict based on prefer list of territory IDs
    rank = dict(enumerate(prefer))
    inv_rank = {v: k for k, v in rank.iteritems()}

    #can help and used to pipe output into text file  ( > log.txt)
    verbose = False # set to False if we don't want any printing at all
    verbose_on_turn_type = 'Fortify' # (ALL, PreAssign, PrePlace, Place, Attack, Occupy, Fortify, TurnInCards)
    state_verbose  = False # for basic info based on state. (at start of turn)

#--------------------------------------------------------------------------------------------------------------#

    if state.turn_type == 'PreAssign':
        if state_verbose:
            print_state_info(state, Board = False)

        verbose = get_verbose(verbose,verbose_on_turn_type,state.turn_type)
        ranking = None

        rank_action = None
        if verbose:

            for key, value in sorted(rank.iteritems(), key=lambda (k,v): (k,v)):
                print "%s: %s" % (key, value), '[', state.board.territories[value].name, ']'

            print '\nPreAssign Allowed Actions (Territories)\n'
            print '\tRANKING\t\tTERRITORY'

        for a in actions:
            curr_rank = inv_rank[state.board.territory_to_id[a.to_territory]]
            if verbose:
                print '\t ',curr_rank,'\t[', a.to_territory ,'|',state.board.territory_to_id[a.to_territory],']'
            if ranking is None or curr_rank < ranking:
                ranking = curr_rank
                rank_action = a
            
        if verbose:
            print '\n PREASSIGN ACTION SELECTION ====', rank_action.to_territory, '\n'

        # print 'action',rank_action.to_territory
        return rank_action

#--------------------------------------------------------------------------------------------------------------#
    elif state.turn_type == 'PrePlace':
        if state_verbose:
            print_state_info(state, Board = False)

        verbose = get_verbose(verbose,verbose_on_turn_type,state.turn_type)
        if free_armies <= 1:
            max_army = {}
            for a in actions:
                if a.to_territory is not None:
                    if not a.to_territory in max_army:
                        max_army[str(a.to_territory)] = state.armies[state.board.territory_to_id[a.to_territory]]

            strong_territory = max(max_army,key=max_army.get)
            #return action
            for a in actions:
                if a.to_territory == strong_territory:
                    return a

        #######################################################################################

        susceptible_pick = {}
        decision_list = []

        if verbose:
            print '\nPrePlace or Place Allowed Actions (Territories)\n'

        for a in actions:
            if a.to_territory is not None:

                neighborhood = state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors
                
                if verbose:
                    print '-----------------------------------------'
                    print 'TURN TYPE :', turn_type, 'IN', a.to_territory
                    print '-----------------------------------------'
                    print 'neighborhood',neighborhood

                for n in neighborhood:
                    if verbose:
                        print 'neighbor ID: ', n, ' owner ID:', state.owners[n], 'owner Name:', state.board.id_to_player[state.owners[n]]
                    if state.owners[n] != state.current_player:
                        if a.to_territory in susceptible_pick:
                            susceptible_pick[a.to_territory] += 1
                        else:
                            susceptible_pick[a.to_territory] = 1
            else:
                print '!!!!!!!action to territory field is None'

        if verbose:
            print '-----------------------------------------'
       
        # make a list of options based on our desire interval 
        for key, value in sorted(susceptible_pick.iteritems(), key=lambda (k,v): (v,k)):
            if verbose:
                print "%s: %s" % (key, value)
            if value <= upper_bound and value >= lower_bound:
                decision_list.append(str(key))

        # if no candidates consider all.
        if len(decision_list) == 0:
            # print 'ZEROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO'
            for key, value in sorted(susceptible_pick.iteritems(), key=lambda (k,v): (v,k)):
                if verbose:
                    print 'key', key, 'value', value
                decision_list.append(key)

        # make random selection of territory candidate
        random.shuffle(decision_list)
        mydecision = random.choice(decision_list)    


        # locate action based on selection and return it 
        for a in actions:
            if a.to_territory == mydecision:
                if verbose:
                    print '\nDecision list \n', decision_list
                    print '\n',turn_type,' ACTION SELECTION ====', mydecision, '\n'
                return a

#######################################################################################################

    elif state.turn_type == 'Place':
        if state_verbose:
            print_state_info(state, Board = False)

        verbose = get_verbose(verbose,verbose_on_turn_type,state.turn_type)
        #######################################################################################
        # if free_armies <= 3:
        #     max_army = {}
        #     for a in actions:
        #         if a.to_territory is not None:
        #             if not a.to_territory in max_army:
        #                 max_army[str(a.to_territory)] = state.armies[state.board.territory_to_id[a.to_territory]]
        #     strong_territory = max(max_army,key=max_army.get)
        #     #return action
        #     for a in actions:
        #         if a.to_territory == strong_territory:
        #             return a
        #######################################################################################
        #Count territories owned by the current player
        territory_num = state.owners.count(player_id)

        #
        owned_continent = {}

        #See if we own any continents
        continent_troops = 0
        for c in state.board.continents.itervalues():
            owned = True
            terr = list()
            for t in c.territories:
                if state.owners[t] != player_id:
                    owned = False
                    break
                else:
                    terr.append(t)
            if owned:
                owned_continent[str(c.name)] = list(terr)



        not_owned_continent = {}

        for c in state.board.continents.itervalues():
            if not str(c.name) in owned_continent:
                not_owned_continent[str(c.name)] = list(c.territories)


        if verbose:
            print 'TESTING CONTINENTS ________________---------------------------------------------------------------------------------'
            print owned_continent
            print 'also---------------------------------------'
            print 'not owned'
            print not_owned_continent


            for c,v in not_owned_continent.iteritems():
                count = 0
                num_terr = len(v)
                if verbose:
                    print 'Number of territories in ', c, 'is', num_terr
                for t in v:
                    if state.owners[t] == player_id:
                        count += 1
                threshold = float(count) / float(num_terr)
                if verbose:
                    print 'Number of territories we own :', count
                    print 'percentage', threshold
                    print '\n'
                    
                if threshold >= 0.75:
                    if verbose:
                        print 'Continent', c, 'Meets threshold (0.60)'
                    
                    old_count = None
                    t_choice = None

                    for t in v:
                        if verbose:
                            print 'looking at ', t, 'which is', state.board.territories[t].name, 'Owner is', state.board.id_to_player[state.owners[t]]
                        
                        enemy_count = 0
                        
                        if state.owners[t] == state.current_player:
                        
                            neighborhood = state.board.territories[t].neighbors
                        
                            if verbose:
                                print 'neighborhood of t', neighborhood
                        
                            for n in neighborhood:
                        
                                if verbose:
                                    print 'looking at neighboor', n, 'which is', state.board.territories[n].name
                        
                                if state.owners[n] != state.current_player:
                        
                                    enemy_count +=1
                            if verbose:
                                print 'total enemy count ', enemy_count

                            if enemy_count != 0:
                                if old_count is None or old_count > enemy_count:
                            
                                    old_count = enemy_count
                            
                                    t_choice = t
                            if verbose:
                                print '\n'
                        
                        else:
                            if verbose:
                                print 'We do not own', t, 'which is', state.board.territories[t].name, 'Owner is', state.board.id_to_player[state.owners[t]]

                    if verbose:
                        print 't_choice ', t_choice, 'which is', state.board.territories[t_choice].name
                        print 'Final t choice is', t_choice


                    #return action immediate that meets criteria
                    for a in actions:
                        if a.to_territory == state.board.territories[t_choice].name:
                            print '\n',turn_type,' ACTION SELECTION ====', a.to_territory, '\n'
                            return a
                    
                else:
                    if verbose:
                        print 'Continent', c, 'DOES NOT MEET THRESHOLD'


        #######################################################################################

        susceptible_pick = {}
        decision_list = []

        if verbose: 
            print '\nPrePlace or Place Allowed Actions (Territories)\n'

        for a in actions:
            if a.to_territory is not None:

                neighborhood = state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors
                
                if verbose:
                    print '-----------------------------------------'
                    print 'TURN TYPE :', turn_type, 'IN', a.to_territory
                    print '-----------------------------------------'
                    print 'neighborhood',neighborhood

                for n in neighborhood:
                    if verbose:
                        print 'neighbor ID: ', n, ' owner ID:', state.owners[n], 'owner Name:', state.board.id_to_player[state.owners[n]]
                    if state.owners[n] != state.current_player:
                        if a.to_territory in susceptible_pick:
                            susceptible_pick[a.to_territory] += 1
                        else:
                            susceptible_pick[a.to_territory] = 1
            else:
                print '!!!!!!!action to territory field is None'



        if verbose:
            print '-----------------------------------------'
       
        # make a list of options based on our desire interval 
        for key, value in sorted(susceptible_pick.iteritems(), key=lambda (k,v): (v,k)):
            if verbose:
                print "%s: %s" % (key, value)
            if value <= upper_bound and value >= lower_bound:
                decision_list.append(str(key))

        # if no candidates consider all.
        if len(decision_list) == 0:
            # print 'ZEROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO'
            for key, value in sorted(susceptible_pick.iteritems(), key=lambda (k,v): (v,k)):
                if verbose:
                    print 'key', key, 'value', value
                decision_list.append(key)

        # make random selection of territory candidate
        random.shuffle(decision_list)
        mydecision = random.choice(decision_list)
        

        # locate action based on selection and return it 
        for a in actions:
            if a.to_territory == mydecision:
                if verbose:
                    print '\nDecision list \n', decision_list
                    print '\n',turn_type,' ACTION SELECTION ====', mydecision, '\n'
                return a

#######################################################################################################

    elif state.turn_type == 'TurnInCards':
        #beginning of turn... 5 cards you have to turn in.. <5 match cards .. you have choice...
        if state_verbose:
            print_state_info(state, Board = False)

        verbose = get_verbose(verbose,verbose_on_turn_type,state.turn_type)

        if verbose:
            print 'TurnInCards'
            print '================================================================'
        for a in actions:
            if verbose:
                print '--------------------------------------------'
                print a.print_action()
                print '--------------------------------------------'
            if a.from_territory != None and a.to_territory != None and a.troops !=None:

                for card in state.board.cards:
                    if card.id == a.from_territory or card.id == a.to_territory or card.id == a.troops:
                        if verbose:
                            print '\n card id', card.id
                            print '\t picture', card.picture
                            print '\t territory id', card.territory, ' --->', state.board.territories[card.territory].name

        if verbose:
            print '================================================================================='
        return actions[0]


        # return getTurnInCardsActions(state)
#######################################################################################################
    elif state.turn_type == 'Attack':

        if state_verbose:
            print_state_info(state, Board = False)

        verbose = get_verbose(verbose,verbose_on_turn_type,state.turn_type)

        pick_by_armies = {}

        if len(actions) == 1:
            return actions[-1]

#######################################################################################################
        # if conquered_territory:
            # return actions[-1]

#######################################################################################################
        for a in actions:
            if a.to_territory is not None:
                if not a.from_territory in pick_by_armies:
                    pick_by_armies[str(a.from_territory)] = state.armies[state.board.territory_to_id[a.from_territory]]

        while not len(pick_by_armies) == 0:                

            strong_territory = max(pick_by_armies, key=pick_by_armies.get)
            
            strong_territory_armies =  pick_by_armies[strong_territory]
            neighborhood = state.board.territories[state.board.territory_to_id[strong_territory]].neighbors

            cutoff = math.ceil(strong_territory_armies * percent_armies)

            #in case 1,2,3,4,5
            if strong_territory_armies == 1 or strong_territory_armies == 2:
                return actions[-1]
            elif strong_territory_armies == 3 or strong_territory_armies == 4:
                cutoff = 1
            elif strong_territory_armies == 5:
                cutoff = 2

            # will show all territories we own with corresponding number of armies in it.
            if verbose:
                print '-----------------------------------------'
                for key, value in sorted(pick_by_armies.iteritems(), key=lambda (k,v): (v,k)):
                    print "%s: %s" % (key, value)
                print '-----------------------------------------'
                print 'strongest territory:', strong_territory, 'with', strong_territory_armies, 'armies'
                print 'percentage of armies:', percent_armies
                print 'cutoff:', int(math.ceil(cutoff))
                print '-----------------------------------------'
                print 'neighborhood', neighborhood       

            for n in neighborhood:
                if verbose:
                    print '|neighbor ID: |', n, '|',state.board.territories[n].name,'|owner ID: ', \
                        state.owners[n], '|owner Name:', state.board.id_to_player[state.owners[n]], '|armies', state.armies[n]

                armies = state.armies[n]
                if state.owners[n] != state.current_player and armies <= cutoff:
                    # we meet criteria , find action to ATTACK
                    for a in actions:
                        if a.from_territory == strong_territory and a.to_territory == state.board.territories[n].name:
                            if verbose:
                                print '\n',turn_type,' ACTION SELECTION ==== FROM:',a.from_territory,'TO:',a.to_territory, '\n'
                            return a

            #no candidate found, keep checking
            del pick_by_armies[strong_territory]

        if verbose:
                print 'No success in finding candidate'


        # If no success in finding an candidate territory to attack , do nothing
        return actions[-1]


#######################################################################################################

    elif state.turn_type == 'Occupy':
        #if you win ,,, leave 1 in used to be terrority...
        if state_verbose:
            print_state_info(state, Board = False)

        verbose = get_verbose(verbose,verbose_on_turn_type,state.turn_type)

        if verbose:
            for a in actions:   
                print '--------------'
                print a.print_action()
                print 'armies',a.troops
                print '--------------'

        #for now return the highest number of troops we can move into 

        return actions[-1]
        # if len(actions) > 8:
        #     return actions[-3]
        # else:
        #     return actions[-1]

        # return getOccupyActions(state)
#######################################################################################################

    elif state.turn_type == 'Fortify':
        #1 fortify move after your done attacking
        # to from and number of troops 
        if state_verbose:
            print_state_info(state, Board = False)

        verbose = get_verbose(verbose,verbose_on_turn_type,state.turn_type)

        if verbose:
            for a in actions:
                # print a.print_action()
                print turn_type , 'FROM:', a.from_territory, 'TO:', a.to_territory, 'NUM', a.troops

        pick = {}
        decision_list = []
        susceptible_pick = {}

        for a in actions:

            from_terr = str(a.from_territory)

            to_terr = str(a.to_territory)

            num_troops = a.troops

            if a.to_territory is not None:

                if not a.from_territory in pick:

                    pick[from_terr] = dict()

                    pick[from_terr][to_terr] = list()

                    pick[from_terr].setdefault(to_terr,[]).append(num_troops)

                else:

                    pick[from_terr].setdefault(to_terr,[]).append(num_troops)

        for k,v in pick.iteritems():
            if verbose:
                print '\nFortify FROM: \t', k
            for to_terr in v:
                neighborhood = state.board.territories[state.board.territory_to_id[to_terr]].neighbors
                if verbose:
                    print '\tTO:',to_terr
                    print 'neighborhood', neighborhood

                for n in neighborhood:
                    if verbose:
                        print 'neighbor ID: ', n, ' owner ID:', state.owners[n], 'owner Name:', state.board.id_to_player[state.owners[n]]
                    if state.owners[n] != state.current_player:
                        if to_terr in susceptible_pick:
                            susceptible_pick[to_terr] += 1
                        else:
                            susceptible_pick[to_terr] = 1


        # print susceptible_pick


        for key, value in sorted(susceptible_pick.iteritems(), key=lambda (k,v): (v,k)):
            enemy = max(susceptible_pick,key =susceptible_pick.get)
            val_enemy = susceptible_pick[enemy]
            if value == val_enemy or value == val_enemy + 1:
                decision_list.append(key)

        if verbose:
            print '\n picks \n'
            for key, value in sorted(pick.iteritems(), key=lambda (k,v): (v,k)):
                print "%s: %s" % (key, value)
            print '\n'
            print '\ndecision list \n', decision_list

        if len(decision_list) == 0:
            return actions[-1]
        else:
            mydecision = random.choice(decision_list)
            options = []
            for k,v in pick.iteritems():
                for to_terr in v:
                    if to_terr == mydecision:
                        options.append((k,to_terr,max(pick[k][to_terr])))

            if len(options) > 0:
                for a in actions:
                    if a.from_territory == options[0][0] and a.to_territory == options[0][1] and a.troops == options[0][2]:
                        return a

#######################################################################################################

    myaction = random.choice(actions)
    
    print 'SITUATION WE DID NOT CONSIDER or did not return action----- RETURNING RANDOM ACTION---------------------------------------'    
    return myaction

def get_verbose(verbose,verbose_on_turn_type,turn_type):
    if verbose == True and verbose_on_turn_type == turn_type:
        return True
    elif verbose == True and verbose_on_turn_type == 'ALL':
        return True
    else:
        return False

def print_state_info(state,Board=False):
    
    #Get info on Agent
    name = state.players[state.current_player].name
    player_id = state.players[state.current_player].id
    turn_type = state.turn_type
    free_armies = state.players[state.current_player].free_armies
    cards = state.players[state.current_player].cards
    conquered_territory = state.players[state.current_player].conquered_territory
    
    #Get array of RiskCard objects (cards) 
    board_cards = list(state.board.cards)

    #Get the possible actions in this state
    actions = getAllowedActions(state)

    if Board:
        print '++++++++++++++++++++++++++++++++++ BOARD INFO ++++++++++++++++++++++++++++++++++'
        print state.board.print_board()
        print '++++++++++++++++++++++++++++++++++ BOARD INFO ++++++++++++++++++++++++++++++++++'

    print '================================================================================== '
    print '****************************** BASIC INFO **************************************** '
    print '***********************',name, 'id:',player_id,' BASIC INFO ************************ '
    print '================================================================================== '
    print '================================================================================== '
    print 'Number of Available actions : ', len(actions)
    print 'Currently in Turn Type :', turn_type
    print 'Number of free armies count ', free_armies
    print 'Cards', cards
    for c in board_cards:
        if c.id in cards:
            print 'Card ID ', c.id,' ',c.print_card(state.board)
    print 'Conquered a territory on current turn (conquered_territory flag)', conquered_territory
    print '================================================================================== '
    print '================================================================================== '

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

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