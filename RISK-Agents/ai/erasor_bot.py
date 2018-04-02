from __future__ import division
import riskengine
import riskgui
import random
from aihelper import *
from turbohelper import *


def Assignment(player):
    freeplaces = filter(lambda x:x.player is None, riskengine.territories.values())
    if freeplaces:
        return freeplaces[-1]
    else:
        return None
            
def Placement(player):
    score = 0
    Tscore = 0
    for t in riskengine.territories.values():
        Cscore = 0
        if TIsFront(t):
            pt,pa,et,ea = CAnalysis(TContinent(t))
            if ea == 0:
                ent = TStrongestFront(t);
                Cscore = 0.0001
                if PHuman(TOwner(ent)):
                    coef = 0.4
                else: 
                    coef = 0.1
                if COwner(TContinent(ent)) is not None :
                    coef += 1.1
                else:
                    coef += 1
                if t.armies * 1.0/ ent.armies < coef:
                    Cscore = 12
            else:
                Cscore = (pt * 1.0/ CTerritoriesCount(TContinent(t))) + 1.0 * pa / ea + (1.0/(CTerritoriesCount(TContinent(t))-pt))*10
            if Cscore > score:
                score = Cscore
                continent = TContinent(t)
    Tscore = -10000
    Score = -10000
    Maxratio = -10000
    
    for t in [x for x in riskengine.territories.values() if x.continent == continent]:
         if TIsFront(t):
             pt,pa,et,ea = CAnalysis(TContinent(t))
             if ea == 0:
                 Tscore = TPressure(t) - t.armies
             for u in [x for x in riskengine.territories.values() if x.continent == continent]:  
                if ea != 0:
                    if u.player != player and TIsBordering(t, u):  
                        Tscore = t.armies - u.armies
                if Tscore >= Maxratio:
                    Maxratio = Tscore
             if Maxratio > Score:
                   Score = Maxratio
                   Tto = t
               
    return Tto
    
def Attack(player):
    Coef = 1.3 + len(riskengine.players)/20
    Tdepart = None
    Tarrive = None
    for t in riskengine.territories.values():
        Tscore = -10000
        if TIsFront(t) and t.armies > 2:
            pt,pa,et,ea = CAnalysis(t)
            for u in [x for x in riskengine.territories.values() if x.continent == TContinent(t)]:
                if ea != 0:
                    if TIsBordering(t, u) and u.player != player:
                        Tscore = t.armies * 1.0 / u.armies
                        arrive = u
                if ea == 0:    
                    if (TPressure(t)*(1.3+(len(riskengine.players)/20))) < t.armies:
                        ent = TWeakestFront(t)
                        Tscore = 1.0 * t.armies / ent.armies
                        arrive = ent
            if Tscore > Coef:
                Coef = Tscore
                Tarrive = arrive
                Tdepart = t
    if Tdepart is not None and Tarrive is not None:
        return Tdepart, Tarrive
    return None, None
    
def Occupation(player, t1, t2):
    if TIsFront(t1) and TIsFront(t2):
        return (t1.armies - t2.armies) // 2
    if TIsFront(t1):
        enemyt = TStrongestFront(t1);
        if enemyt.armies > t1.armies:
            return 1
        elif enemyt.armies < t1.armies:
            return t1.armies - enemyt.armies
    return t1.armies - 2
    

def Fortification(player):
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
    
    val = 0
    for t in FromTerr.neighbors:
        if TIsFront(t):
            nval = TPressure(t) * 1.0 / t.armies
            if nval > val:
                val = nval
                ToTerr = t
    
    if ToTerr is None:
        for t in FromTerr.neighbors:
            if t.player == player:   
                ToTerr = t
                break
    if ToTerr is not None:
        return FromTerr, ToTerr, FromTerr.armies - 1
    return None
 
 
      