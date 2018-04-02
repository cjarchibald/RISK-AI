import riskengine
import riskgui
import random
from aihelper import *
from turbohelper import *
from risktools import *

continent_priorities = {'S. America' : 7,
                        'N. America' : 4,
                        'Africa' : 4,
                        'Europe' : 4,
                        'Asia' : 1,
                        'Australia' : 0}

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""

    #Get the possible actions in this state
    actions = getAllowedActions(state)

    #Do nothing by default
    myaction = actions[-1]

    if state.turn_type == 'Attack':
        possible_action = None
        action_ratio = 1.75 #Minimum ratio to attack
        for a in actions:
            if a.to_territory is not None and a.from_territory is not None: #If it is an attack
                my_armies = state.armies[state.board.territories[state.board.territory_to_id[a.from_territory]].id]
                enemy_armies = state.armies[state.board.territories[state.board.territory_to_id[a.to_territory]].id]
                ratio = float(my_armies) / float(enemy_armies)  #ratio of my armies vs enemy armies
                if ratio > action_ratio:    #If the ratio is higher
                    possible_action = a     #Thats the action we'll take
                    action_ratio = ratio    #New ratio
        if possible_action is not None:     #Thers's an attack to do
            myaction = possible_action      #Just Do it

    if state.turn_type == 'PreAssign':
        possible_actions = []               #Possible territories to take
        possible_desirablity = 0            #Value to hold desirablity of the action we take
        for a in actions:
            action_desirablity = 0          #Value to hold desirablity of the action we are testing
            con_name = None                 #Name of the continents the territory is on
            if a.to_territory is not None:
                terr = state.board.territories[state.board.territory_to_id[a.to_territory]]
                for con in state.board.continents.values():
                    if terr.id in con.territories:  #If the territory is in the continent's territories
                        con_name = con.name
                        break   #Exit as the value is known

                action_desirablity += continent_priorities[con_name]    #Assigns the desirablity based on continet

                for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] == state.current_player:     #If the territory is a neighbor to a territory already ours
                        action_desirablity += 2                     #Adds more to the desirablity
                        break

            if action_desirablity == possible_desirablity:          #The territory is as desirable as our current best, throw it in the list of possible actions
                possible_actions.append(a)

            elif action_desirablity > possible_desirablity:         #If it is more desirable get rid of the previous best options
                possible_actions = []                               #Get rid of the previous best actions
                possible_actions.append(a)                          #Add it to the possible actions
                possible_desirablity = action_desirablity           #Set the current most desirable value to this action's desirablity

        if len(possible_actions) > 0:
            myaction = random.choice(possible_actions)              #Get's the action taken

    if state.turn_type == 'TurnInCards':
        crds = state.players[state.current_player].cards
        for a in actions:
            if a.to_territory in crds and a.from_territory in crds and a.troops in crds:
                if isCardSet(state, a.to_territory, a.from_territory, a.troops):
                    myaction = a
                    break

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

def TargetC(player):
    # LOCAL FUNCTION TARGETC:  determines the target continent to attack
    # best ratio of armies in the continent and its borders
    BestDiff=SMALL
    for C in riskengine.continents:
        PT =0
        PA =0
        ET =0
        EA = 0
        PT, PA, ET, EA =CAnalysis(C)
        if ET>0:
            # sub CBORDERANALYSIS:  adjust PT, PA, ET, and EA to reflect
            # territories that border the given continent
            for T in CBorders(C):
                if TIsMine(T):
                  PT = PT+1
                  PA = PA+T.armies
                else:
                  ET = ET+1
                  EA = EA+T.armies
        Diff = PA-ET-EA
        if ET>0 and PT>0 and Diff>BestDiff:
            BestDiff = Diff
            BestC = C
 #      UMessage(BestC)      UMessage(BestDiff)
    return BestC

def MyTPressure(t,MaxFronts):
    # LOCAL FUNCTION MYTPressure:  returns available armies bordering on [enemy?] territory T
    # my territories must have at most MaxFronts fronts in order to count its armies
    Pressure = 0
    for MyT in t.neighbors:
        if TIsMine(MyT) and len(MyT.neighbors) <= MaxFronts:
            Pressure = Pressure + MyT.armies
    return Pressure

def TargetT(player, enemyc):
    # LOCAL FUNCTION TARGETT:  determines the target territory to attack
    # will return a territory on another continent if no attacks are available
    # on the desired continent {can also return 0 if no feasible attack is available at all}
    # uses local global ENEMYC
    BestDiff = SMALL
    BestT = None
    for t in filter(lambda x:x==enemyc,riskengine.territories.values()):

    #      UMessage('Checking out territory #',X,' of target continent ',ENEMYC)
        y = MyTPressure(t, ALLFRONTS)
    #      UMessage('Looking at territory ',T,' which you have ',Y,' total pressure on')
        if y>0 and FORCE*t.armies<player.freeArmies + y and not TIsMine(t):
          # if its an enemy territory that can be conquered, then compute
          # your 1-front armies (+) less attacked armies (-) less new exposure to enemies (-)
            Diff = MyTPressure(t,ONEFRONTS)-t.armies
    #          UMessage('Initial Diff (1-front armies less attacked) is ',Diff)
            for t2 in t.neighbors:
    #              UMessage('Secondary loop, looking at territory #',Y,' (namely ',T2,') with my pressure of ',MyTPressure(T2,ALLFRONTS),' and armies ',TArmies(T2))
                if MyTPressure(player, t2,ALLFRONTS)==0 and not TIsMine(t2):
                    Diff = Diff-t2.armies
              # new exposure when territory is conquered
    #          UMessage('A conquerable territory on target continent ',EnemyC,' is ',T)
    #          UMessage('my [wasted] 1-front armies less attacked armies less new exposures is ',Diff)
            if Diff>BestDiff:
                BestDiff = Diff
                BestT = T
    if BestT is None:
      # look for easiest territory that can be taken [may be on another continent]

      for T in riskengine.territories.values():
          if TIsMine(T):
              ET = TWeakestFront(T)
              Diff = TArmies(T)-TArmies(ET)
              if Diff>BestDiff:
                  BestDiff = Diff
                  BestT = ET

    #      TWeakestFront(BestT,ET,EA)
    #      Diff = PNewArmies(player)*NEWRATIO # allow only a %-age of new armies to go for this attack
    #      Diff = Diff+TArmies(BestT)-EA*FORCE
    #      if Diff<1 then BestT = 0
    return BestT

def Placement(player):
    # PLACEMENT:  defines ToTerritory (where 1 army will be placed)
    # 1) make sure ANY attack is possible
    # 2) reinforce existing continents
    # 3) make sure desired attack is possible
    # 4) beef up the target continent
    # 5) take care of the rest of your territories
    global SMALL, FORCE, MINARMIES, ALLFRONTS, ONEFRONTS, CBONUS, NEWRATIO, enemyc

    SMALL = -9999       # CONSTANTS SECTION
    FORCE = 1.2
    MINARMIES = 5
    ALLFRONTS = 10
    ONEFRONTS = 1
    CBONUS = 12          # bonus for reinforcing territories in current target continent
    NEWRATIO = 0.5      # %-age of new armies that can go towards an out-of-continent attack

    ToTerritory = None
    AnyAttack = 0
    for T in riskengine.territories.values():
        if TIsMine(T):
            ET = TWeakestFront(T)
            if (T.armies>MINARMIES+TArmies(ET)*FORCE):
                AnyAttack = 1

    for C in riskengine.continents: # reinforce existing continents if necessary - to defend against STRONGEST front first
        if (COwner(C)==player) and (ToTerritory is None) and (AnyAttack==1):
            for T in CTerritories(C):
                if TIsFront(T):
                    et = TStrongestFront(T)
                    if (T.armies<MINARMIES+et.armies*FORCE): # shortfall in my territory T
                        if (ToTerritory is None):
                            ToTerritory = T
                        elif (T.armies>ToTerritory.armies):
                            ToTerritory = T

    EnemyC = TargetC(player)
    EnemyT = TargetT(player, EnemyC)

    #  UMessage('Total new armies to place ',PNewArmies(player))
    #  UMessage('target continent = ',EnemyC)
    #  UMessage('target territory = ',EnemyT)
    #  UMessage('total pressure on that target territory = ',MyTPressure(EnemyT,ALLFRONTS))
    #  UMessage('minimum required armies to attack = ',MINARMIES+TArmies(EnemyT)*FORCE)


    if (EnemyT) and (MyTPressure(EnemyT,ALLFRONTS)<(MINARMIES+EnemyT.armies*FORCE)):
        # continue to reinforce until attack is possible - put them all in strongest country
        BestDiff = SMALL
        for T in EnemyT.neighbors:
            Diff = T.armies
            if TIsFront(T) and (Diff>BestDiff):
                BestDiff = Diff
                ToTerritory = T

    if (ToTerritory is None): # attack is already guaranteed.  beef up the target continent
        PT = 0
        PA = 0
        ET = 0
        EA = 0
        BestDiff = SMALL
        PT, PA, ET, EA = CAnalysis(player, EnemyC)
        if ((PA-PT)<MINARMIES+ET+EA*FORCE):
         # place more armies in the continent so that you can capture the whole thing
            for T in CTerritories(EnemyC):
                Diff = T.armies # put in strongest
                if (PNewArmies(player)>5):
                    Diff = -TArmies(T)  # but put in weakest front until 5 armies left
                if TIsFront(T) and (Diff>BestDiff):
                    ToTerritory = T
                    BestDiff = Diff

    for C in riskengine.continents: # reinforce existing continents if necessary - WEAKEST front first
        if (COwner(C)==player) and (ToTerritory is None): # if you own the continent and already have an attack
            for T in CTerritories(C):
                if TIsFront(T):
                    et = TStrongestFront(T)
                    if (TArmies(T)<et.armies*FORCE):
                        if (ToTerritory is None):
                            ToTerritory = T
                    elif (TArmies(T)>TArmies(ToTerritory)):
                        ToTerritory = T


    ET = TWeakestFront(EnemyT)
    EA = TArmies(ET)
    if (EnemyT) and (ToTerritory is None) and (MyTPressure(EnemyT,ALLFRONTS)<(EA+MINARMIES+TArmies(EnemyT)*FORCE)):
        # continue to reinforce until attack is possible - put them all in strongest country
        BestDiff = SMALL
        for T in EnemyT.neighbors:
            if TIsMine(T) and (TArmies(T)>BestDiff):
                BestDiff = TArmies(T)
                ToTerritory = T
    for C in riskengine.continents:# reinforce existing continents if necessary
        if COwner(C) == player and ToTerritory is None:# if you own the continent and already have an attack
            for T in CTerritories(C):
                if TIsFront(T):
                    if (TArmies(T)<TPressure(T)*FORCE):
                        if (ToTerritory is None):
                            ToTerritory = T
                        elif (TArmies(T)>TArmies(ToTerritory)):
                            ToTerritory = T



    if ToTerritory is None: # attack is already guaranteed
        BestDiff = SMALL
        for T in riskengine.territories.values():
            ET = TWeakestFront(T)
            EA = TArmies(ET)
            Diff = TArmies(T)+PNewArmies(player)-EA # worthwhile to fortify this one?
            if (TContinent(T)==EnemyC):
                Diff = 1 # but always worthwhile fortifying your target continent
            if TIsFront(T) and (Diff>0):# territory is mine and front and can be made stronger than the weakest front
                Diff =  TPressure(T)-TArmies(T)
                if TIsBordering(T,EnemyT):
                    Diff = TPressure(T)+(TArmies(T) // 8) # avoid fortifying around a country you're about to take
                if (TContinent(T)==EnemyC):
                    Diff = Diff+CBONUS
    #              UMessage('Territory ',T,' is worthy of fortification with Pressure - Armies + Bonus of ',Diff)
                if (Diff>BestDiff):
                    ToTerritory = T
                    BestDiff = Diff
    return ToTerritory


def Attack(player):
 #Need to return the name of the attacking territory, then the name of the defender territory
    return aiWrapper('Attack')


def Occupation(player,t1,t2):
    if TIsFront(t1) and TIsFront(t2):
        return (t1.armies - t2.armies) // 2
    if TIsFront(t1):
        return 0

    return t1.armies - 1

def Fortification(player):
    return aiWrapper('Fortification')
