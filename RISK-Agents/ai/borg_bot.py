import riskengine
import riskgui
import random
from aihelper import *
from turbohelper import *

amborg = 1
    
    
def IsBorg(otherplayer):
    return hasattr(otherplayer.ai, "amborg")
    
def MyTIsFront(terr, player=None):
    if player is None: player = riskengine.currentplayer
    if terr.player != player:
        return 0
    if not [x for x in terr.neighbors if x.player != player and not IsBorg(x.player)]:
        return 0
    return 1

def MyTPressure(terr, player=None):
    if player is None: player = riskengine.currentplayer
    pr = 0
    for i in terr.neighbors:
        if i.player != player and not IsBorg(i.player):
            pr += i.armies
    return pr

def MyTWeakestFront(t, pl=None):
    if pl is None: pl = riskengine.currentplayer
    arms = 1000
    terr = None
    for i in t.neighbors:
        if i.player != pl and not IsBorg(i.player):
            if i.armies < arms:
                arms = i.armies
                terr = i
    return terr

def Assignment(player):
    freeplaces = filter(lambda x:x.player is None, riskengine.territories.values())
    if (freeplaces):
        return freeplaces[0]
    else:
        return None
            
def Placement(player):
    MaxRatio = 0
    Tto = None
    for t in riskengine.territories.values():
        if MyTIsFront(t):
            Ratio = MyTPressure(t) * 1.0 / t.armies
            if Ratio > MaxRatio:
                MaxRatio = Ratio
                Tto = t
    return Tto
    
def Attack(player):
    if player.conqueredTerritory == 1:
        return None,None
    FromTerr = None
    ToTerr = None
    MaxRatio = 0
    for t in riskengine.territories.values():
        if MyTIsFront(t) and t.armies > 1:
            te = MyTWeakestFront(t)
            ratio = t.armies * 1.0 / te.armies
            if ratio > MaxRatio:
                MaxRatio = ratio
                FromTerr = t
                ToTerr = te
    return FromTerr, ToTerr
    
def Occupation(player, t1, t2):
    if MyTIsFront(t1) and MyTIsFront(t2):
        return (t1.armies - t2.armies) // 2
    if MyTIsFront(t1):
        return 0
    
    return t1.armies - 1
    

def Fortification(player):
    FromTerr = None
    ToTerr = None
    Armies = None
    
    MaxArmy = 1
    for t in riskengine.territories.values():
        if t.player == player and not MyTIsFront(t):
            if t.armies > MaxArmy:
                MaxArmy = t.armies
                FromTerr = t
                
    if FromTerr is None:
        return None, None, 0
        
    for t in FromTerr.neighbors:
        if MyTIsFront(t):
            ToTerr = t
            break
    
    if ToTerr is None:
        for t in FromTerr.neighbors:
            if t.player == player:   
                ToTerr = t
                break
    
    return FromTerr, ToTerr, FromTerr.armies - 1
    