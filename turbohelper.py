"""This file helps match ai's based upon 
TurboRisk ai's to work in this game
"""

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
import riskgui

def run_preplace(player):
    """Runs when the player is supposed to select 
    and support his first territory
    """
    riskengine.logai("run_preplace")
    freeplaces = [x for x in riskengine.territories.values() if x.armies == 0]
    if freeplaces:
        terr = player.ai.Assignment(player)
        if terr is not None and terr.armies == 0:
            player.place_army(terr)
            riskgui.drawterritory(terr, 0)
        else:
            riskengine.logai("AI " + player.name + " couldn't place armies, gave up")
            

    else:
        terr = player.ai.Placement(player)
        if terr is not None:  
            player.place_army(terr)
            riskgui.drawterritory(terr, 0)
        else:
            riskengine.logai("AI" + player.name + "couldn't place armies, gave up")

def do_cards(player):
    card_function = getattr(player.ai, "TurnInCards", None)
    print 'Trying to do cards. The card function is: ', card_function
    if callable(card_function):
        c1, c2, c3 = card_function(player)
        if c1 is not None:
            riskengine.logai("turning in cards")
            riskengine.turnincards(player, [c1, c2, c3])
    if len(player.cards) >= 5:
        do_auto_cards(player)

def do_auto_cards(player):
    """Turn in all of a player's cards"""
    if len(player.cards) >= 5:
        for a in range(len(player.cards)-2):
            for b in range(a+1, len(player.cards) - 1):
                for c in range(b+1, len(player.cards)):
                    if riskengine.cardset([player.cards[a], 
                                           player.cards[b], 
                                           player.cards[c]]):
                        riskengine.logai("turning in cards")
                        riskengine.turnincards(player, [player.cards[a], 
                                                        player.cards[b], 
                                                        player.cards[c]])
                        return

def run_place(player):
    """Place a player's units at the beginning of the turn"""
    #See if the AI wants to turn in cards
    if len(player.cards) >= 3:
        do_cards(player)        
        
    while len(player.cards) >= 5:
        do_cards(player)
        
    for i in range(player.freeArmies):
        terr = player.ai.Placement(player)
        if terr is not None:
            player.place_army(terr)
            riskgui.drawterritory(terr, 0)

def run_attack(player):
    """Have a player run his attacks, and then his fortification"""
    riskengine.logai("run_attack")
    while 1:
        fromterr, toterr = player.ai.Attack(player)
            
        if fromterr is None or toterr is None or fromterr.armies <= 1:
            break
        riskengine.logai("AI %s attacks %s with %s" % 
                            (player.name, toterr.name, fromterr.name))
        riskengine.attack(fromterr, toterr)
        riskgui.drawterritory(fromterr, 0)
        riskgui.drawterritory(toterr, 0)
        
        if toterr.player == player: #we won
            movarm = player.ai.Occupation(player, fromterr, toterr)
            if movarm <= 0:
                continue
            movarm = min(movarm, fromterr.armies - 1)
            fromterr.armies -= movarm
            toterr.armies += movarm
            riskgui.drawterritory(fromterr, 0)
            riskgui.drawterritory(toterr, 0)
    
    fromterr, toterr, armies = player.ai.Fortification(player)
    if fromterr is not None and toterr is not None and armies > 0:
        armies = min(armies, fromterr.armies - 1)
        fromterr.armies -= armies
        toterr.armies += armies
        riskgui.drawterritory(fromterr, 0)
        riskgui.drawterritory(toterr, 0)

def saveddata():
    return ""

def loaddata(indata):
    pass