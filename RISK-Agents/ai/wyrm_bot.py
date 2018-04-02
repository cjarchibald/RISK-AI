from __future__ import division
import riskengine
import riskgui
import random
from aihelper import *
from turbohelper import *


def Assignment(player):
    freeplaces = filter(lambda x:x.player is None, riskengine.territories.values())
    if freeplaces:
        return freeplaces[0]
    else:
        return None
        
        
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
    
    
    
    
    
    
    
    
    
    
    
    
    
def ATargetC(player):
    # LOCAL FUNCTION TARGETC:  determines the target continent to attack
    # best ratio of armies in the continent and its borders
    BestDiff = 0
    Y=None
    for X in riskengine.players.values():
        if (X != player):
            if (PArmiesCount(X)>BestDiff):
                BestDiff=PArmiesCount(X)
                Y=X # Y holds the leading player's number
    
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
        
        if (COwner(C)==Y) and player.conqueredTerritory and (PT>0): # attack the leading player's continents
            Diff=Diff+500
#          UMessage(PName(player),' is favoring an extra attack on ',PName(Y),', in continent # ',C,', because they are the leader')

        if (COwner(C)) and (COwner(C)!=player) and player.conqueredTerritory and (PT>0):
#        if (PArmiesCount(COwner(C))>PArmiesCount(player)):
          Diff=Diff+500
          
          
        
        if ET>0 and PT>0 and Diff>BestDiff:
            BestDiff = Diff
            BestC = C
 #      UMessage(BestC)      UMessage(BestDiff)
    return BestC

def ATargetT(player, enemyc):
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
    if BestT is None and not player.conqueredTerritory:
      # look for easiest territory that can be taken [may be on another continent]

      for T in riskengine.territories.values():
          if TIsMine(T):
              et = TWeakestFront(T)
              Diff = TArmies(T)-TArmies(et)
              if Diff>BestDiff:
                  BestDiff = Diff
                  BestT = et

    #      TWeakestFront(BestT,ET,EA)
    #      Diff = PNewArmies(player)*NEWRATIO # allow only a %-age of new armies to go for this attack
    #      Diff = Diff+TArmies(BestT)-EA*FORCE
    #      if Diff<1 then BestT = 0
    return BestT    
    
    
def Attack(player):
    # defines FromTerritory and ToTerritory.  No attack if FromTerritory is 0
    # perform an attack on the next achievable continent, or the cheapest attack if
    # no attack is available there (decided in def TargetT).
    # Not Implemented yet:  If you can safely eliminate a player, do so
    # sometimes picks a smaller front when a non-front is available???
    global EnemyC, SMALL, FORCE, MINARMIES, ALLFRONTS, ONEFRONTS, CBONUS, NEWRATIO
    SMALL=-9999       # CONSTANTS SECTION
    FORCE=0.95         # smaller FORCE than in PLACEMENT procedure to encourage attacks
    MINARMIES=2
    ALLFRONTS=10
    ONEFRONTS=1
    CBONUS=5          # bonus for reinforcing territories in current target continent
    NEWRATIO=0.5      # %-age of new armies that can go towards an out-of-continent attack
    
    EnemyC=ATargetC(player)
    PT=0
    PA=0
    ET=0
    EA=0
    PT, PA, ET, EA = CAnalysis(EnemyC)
    FromTerritory = ToTerritory = None

#  if SConquest:
#    UMessage('Target continent== ',EnemyC,' with excess of ',PA-PT-ET-EA)

#  if SConquest and (PA>EA):
#    UMessage('You should attack continent ',EnemyC,' since you have ',PA,' armies and he only has ',EA)

    BestDiff = 0
    for X in riskengine.players.values():
        if (X != player):
            if (PArmiesCount(X)>BestDiff):
                BestDiff=PArmiesCount(X)
                B=X # Y holds the leading player's number


    if ((PA-PT)>((MINARMIES+ET+EA)/FORCE)) or (not player.conqueredTerritory) or (COwner(EnemyC)):
        ToTerritory=ATargetT(player, EnemyC)
#      UMessage('Target Continent== ',EnemyC,' Target Territory== ',ToTerritory)
#      if (ToTerritor==0) and (not SConquest):
#        UMessage('why arent you proposing an attack, perhaps on your target continent ',EnemyC)
#      if SConquest and (ToTerritory<>0):
#        UMessage('Extra attack!  You are attacking continent ',EnemyC,', territory ',ToTerritory,' since you have ',PA,' armies and he only has ',EA)
        if (ToTerritory is not None):
          # calculate the correct territory to attack from
          # 1)  weakest 1-front if ToTerritory armies > 2, otherwise strongest 1-front
          # 2)  highest TArmies-TPressure.  This may not be the best
            BestDiff=SMALL*5
            for T in ToTerritory.neighbors:
                if TIsMine(T) and (TArmies(T)>1) and ((TArmies(T)>2) or (TArmies(ToTerritory)==1)): # no attacks ever with 2 or less armies
                    Diff=TArmies(T)-(TPressure(T) // 3) # stress armies more than pressure
                    if (TArmies(T)<4) and (TArmies(ToTerritory)>1):
                        Diff=Diff+SMALL*2 # discourage these attacks with less than 4 armies
                    if (TFrontsCount(T)==1):
                        if (TArmies(ToTerritory)>2):
                            Diff=Diff-SMALL-TArmies(T)*2  # weakest 1-front will be picked
                        else:
                            Diff=Diff-SMALL # strongest 1-front will be picked
                    if (Diff>BestDiff):
                        BestDiff=Diff
                        FromTerritory=T

            BestDiff=(MyTPressure(ToTerritory,ALLFRONTS))-(TArmies(ToTerritory))
            if (BestDiff<0):
#              UMessage('About to abort an attack on target continent ',EnemyC,' from ',FromTerritory,' to ',ToTerritory,' with enemy armies ',TArmies(ToTerritory),' and MyTPressure ',MyTPressure(ToTerritory,ALLFRONTS),' for a total negative difference of ',BestDiff)
#              UMessage('double checking - enemy armies ',TArmies(ToTerritory),' and MyTPressure ',MyTPressure(ToTerritory,ALLFRONTS),' for a total negative difference of ',BestDiff)
                FromTerritory=None # abort attacks that won't work
    return FromTerritory, ToTerritory










def Occupation(player, FromTerritory, ToTerritory):

    # very simple but effective routine
    # moves ARMIES from FROMTERRITORY to TOTERRITORY (which was just conquered)

    FromIsFront = TIsFront(FromTerritory)
    ToIsFront = TIsFront(ToTerritory)
    Armies=0

    if  FromIsFront and ToIsFront:  # if both territories are 'front'
        ET = TStrongestFront(FromTerritory) # idea is to leave behind only what you need
        EA = ET.armies
        Buffer=TArmies(FromTerritory) // 8
        if (Buffer<3):
            Buffer=3
        EA=EA+Buffer # leave some extra
        ET=(1+TArmies(FromTerritory)-TArmies(ToTerritory)) // 2 # balancing move
        if (EA>TArmies(FromTerritory)-ET):
            Armies=ET # will always move at least armies to balance territories
        else:
            Armies=TArmies(FromTerritory)-EA # but maybe more
    elif FromIsFront: # only "From" territory is front
        pass # all armies stay in From territory, so there's nothing to do
    else:
        # all armies in the conquered territory (except one which must stay)
        Armies=TArmies(FromTerritory)-1
    return Armies
    
    
def Fortification(player):
    global ALLFRONTS, ONEFRONT, SMALL
    FromTerritory=None
    ToTerritory=None
    Armies=0
    ALLFRONTS=10
    ONEFRONTS=1
    SMALL=-9999

    # look for front country that needs the most help.  favor continents that you
    # already own, and countries that can be helped by 0-fronts
    # "most help" implies difference between MyArmies and the strongest front

    # for each of your fronts, determine the FromTerritory, the deficit, and the benefit able to be provided


    BestArmies=0
    BestDiff=SMALL
#  UMessage('Calling procedure Fortification')

    for T in riskengine.territories.values():
        if TIsFront(T):
            ET = TStrongestFront(T)
            EA = ET.armies
            Diff=EA-TArmies(T) # your current deficit
            BestArmies=0
            for F in T.neighbors:
                if TIsMine(F) and (TArmies(F)>1):
                    ET = TStrongestFront(F)
                    EA = TArmies(ET)
                    if (not TIsFront(F)):
                        Arm=TArmies(F)-1
                    else:
                        Arm=TArmies(F)-EA # the absolute most you can spare
#                  UMessage(TName(T),' has a deficit of ',Diff,' but can be helped by ',TName(F),' which can spare ',Arm,' armies')
                    if (Arm>BestArmies):
                        BestArmies=Arm
                        BestFrom=F
            # now you have found your best FromTerritory "BestFrom" for this ToTerritory T
            # it can spare "BestArmies" and you had desired "Diff"
            B=Diff
            if (B>BestArmies):
                B=BestArmies # you needed more than you could can spare
            if (B>BestDiff) and ((B+BestArmies)>1) and (BestArmies>2):
                Armies=(B+BestArmies) // 2
                if (not TIsFront(BestFrom)):
                    Armies=BestArmies
#            UMessage('Found a better fortification:  move ',Armies,' armies from ',TName(BestFrom),' to ',TName(T))
                BestDiff=B
                FromTerritory=BestFrom
                ToTerritory=T
                

#  if (Armies<>0): 
#    UMessage('Recommend moving ',Armies,' from ',FromTerritory,' to ',ToTerritory)

    if (ToTerritory is None): # use original fortification code -- find largest zero-front
        FromTerr = None
        ToTerr = None
        Armies = None
        
        MaxArmy = 1
        for t in riskengine.territories.values():
            if t.player == player and not TIsFront(t):
                if t.armies > MaxArmy:
                    MaxArmy = t.armies
                    FromTerr = t

        if FromTerr is None:
            return None, None, 0

        for t in FromTerr.neighbors:
            if TIsFront(t):
                ToTerr = t
                break

        if ToTerr is None:
            for t in FromTerr.neighbors:
                if t.player == player:   
                    ToTerr = t
                    break
        
        return FromTerr, ToTerr, FromTerr.armies - 1
    return FromTerritory, ToTerritory, Armies
