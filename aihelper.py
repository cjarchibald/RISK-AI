"""This is a risk game, playable over the internet.
Copyright (C) 2004 John Bauman

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""

import riskengine

def TIsFront(t, pl=None):
    if pl is None: pl = riskengine.currentplayer
    if t.player != pl:
        return 0
    if not [x for x in t.neighbors if x.player != pl]:
        return 0
    return 1

def TPressure(t, pl=None):
    if pl is None: pl = riskengine.currentplayer
    return sum([i.armies for i in t.neighbors if i.player != pl])

def TWeakestFront(t, pl=None):
    if pl is None: pl = riskengine.currentplayer
    if t is None: return None
    arms = 1000
    terr = None
    for i in t.neighbors:
        if i.player != pl:
            if i.armies < arms:
                arms = i.armies
                terr = i
    return terr

def TStrongestFront(terr, player=None):
    if player is None: player = riskengine.currentplayer
    arms = -1
    terrout = None
    for i in terr.neighbors:
        if i.player != player:
            if i.armies > arms:
                arms = i.armies
                terrout = i
    return terrout

def TFrontsCount(terr, player=None):
    if player is None: player = riskengine.currentplayer
    return len([x for x in riskengine.territories.values() if x.player != player])

def TIsMine(terr):
    return terr.player == riskengine.currentplayer
    
def TOwner(terr):
    return terr.player

def TArmies(terr):
    if terr:
        return terr.armies
    else: 
        return 0
        
def TContinent(terr):
    return terr.continent

def TIsBordering(terr, terr2):
    return terr.neighboring(terr2)
    
    
    

def toplayer(player):
    if isinstance(player, riskengine.Territory): 
        return player.player
    else:
        return player
    
def PHuman(player):
    player = toplayer(player)
    return not player.ai

def PArmiesCount(player):
    player = toplayer(player)
    return sum([t.armies for t in riskengine.territories.values() if t.player == player])

def PNewArmies(player):
    player = toplayer(player)
    return player.freeArmies
    
    
    

def tocontinent(con):
    if isinstance(con, riskengine.Territory):
        return con.continent
    elif isinstance(con, tuple): 
        return con[0]
    else:
        return con

def COwner(con):
    con = tocontinent(con)
    continentterrs = [x for x in riskengine.territories.values() if x.continent == con]
    try:
        firstowner = continentterrs[0].player
    except:
        print continentterrs, con,riskengine.territories['India'].continent
        raise
    for x in continentterrs:
        if x.player != firstowner:
            return None
    return firstowner
  
def CTerritories(con):
    con = tocontinent(con)
    return [x for x in riskengine.territories.values() if x.continent == con]
    
def CTerritoriesCount(con):
    if isinstance(con, riskengine.Territory): con = con.continent
    if isinstance(con, tuple): con = con[0]
    return len(CTerritories(con)) 
    
def CAnalysis(con, pl=None):
    if pl is None: pl = riskengine.currentplayer
    con = tocontinent(con)
    continentterrs = [x for x in riskengine.territories.values() if x.continent == con]
    myterrs = [x for x in continentterrs if x.player == pl]
    enemyterrs = [x for x in continentterrs if x.player != pl and x.player is not None]
    myarmy = sum([t.armies for t in myterrs])
    theirarmy = sum([t.armies for t in enemyterrs])
    return len(myterrs), myarmy, len(enemyterrs), theirarmy
    
def CBorders(con):
    con = tocontinent(con)
    terrs = []
    for terr in riskengine.territories.values():
        if terr.continent != con:
            if [x for x in terr.neighbors if x.continent == con]:
                terrs.append(terr)
    return terrs
    
    
    

def UMessage(*args):
    riskengine.logai("".join([str(arg) for arg in args]))
    
