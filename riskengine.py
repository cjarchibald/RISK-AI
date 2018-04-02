
"""This code holds the actual engine of the risk game.
It does the computations and drives everything."""

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
import random
import xml.dom.minidom
import zipfile
import imp
import sys
import os.path


import riskgui
import risknetwork


debugging = 0
territories = {}
players = {}
continents = []
ailog = []

mapfile = None



class devnull(object):
    def write(self,str):
        pass
        
def setupdebugging():
    global verbosefile
    if debugging:
        verbosefile = sys.stdout
    else:
        verbosefile = devnull()   

class Territory(object): 
    """Represents a territory"""
    def __init__(self, name, continent, player, neighbors):
        self.name = name
        self.continent = continent
        self.player = player
        self.neighbors = neighbors
        self.armies = 0
        
    def linkreferences(self):
        """Match up the string references into real references."""
        for i in range(len(self.neighbors)):
            self.neighbors[i] = territories[self.neighbors[i]]
    
    def neighboring(self, terr):
        """Check if terr borders this Territory."""
        return terr in self.neighbors
    

def movearmies(territory1, territory2, armies):
    """Move a certain number of armies from one territory to another."""
    if armies < 0 or territory1.armies <= armies:
        return
    
    territory2.armies += armies
    territory1.armies -= armies
        
def changecontrol(territory1, territory2, dice):
    """Change control of an army from one player to another."""
    territory2.player = territory1.player
    movearmies(territory1, territory2, dice)
    

 
def logai(string):
    """Log all the AI debugging info."""
    ailog.append((currentplayer, string))
    print >>verbosefile, currentplayer.name + ": " + string
    
def getlog():
    """Return the log."""
    return ailog
    
def attack(territory1, territory2, army1=-1, army2=-1):
    """Have one territory attack another"""
    if army1 == -1:
        army1 = min(territory1.armies - 1, 3)
    if army2 == -1:
        army2 = min(territory2.armies, 2)
    if army1 < 1 or army1 >= territory1.armies or army1 > 3:
        return
    if army2 < 1 or army2 > territory2.armies or army2 > 2:
        return
    if not [x for x in territory1.neighbors if x == territory2]:
        return
    numdice = min(army1, army2)
        
    dice1 = [random.randint(1, 6) for i in range(army1)]
    dice1.sort()
    dice1.reverse()
    
    dice2 = [random.randint(1, 6) for i in range(army2)]
    dice2.sort()
    dice2.reverse()
    
    if dice1[0] > dice2[0]:
        territory2.armies -= 1
    else:
        territory1.armies -= 1
    
    if numdice == 2:
        if dice1[1] > dice2[1]:
            territory2.armies -= 1
        else:
            territory1.armies -= 1
     
    if territory2.armies == 0:
        oldplayer = territory2.player
        changecontrol(territory1, territory2, army1)
        territory1.player.conqueredTerritory = 1
        if not [x for x in territories.values() if x.player == oldplayer]:
            removeplayer(oldplayer, territory1.player)
            
    assert territory1.armies > 0
    assert territory2.armies > 0




def openworldfile(worldfile):
    """Open up a zip file to get the map data."""
    global zfile, mapfile
    zfile = zipfile.ZipFile(worldfile)
    mapfile = worldfile

def closeworldfile():
    """Close up the map zip file."""
    global zfile
    zfile.close()
    zfile = None

def loadterritories():
    """Load territory (and other) information from a file."""
    global territories, continents
    territories = {}
    continents = []
    
    terr = xml.dom.minidom.parseString(zfile.read("territory.xml"))
    
    terr_structs = terr.getElementsByTagName("territory")
    for terrs in terr_structs:
        name = terrs.getAttribute("name")
        continent = terrs.getAttribute("continent")
        neighbors = terrs.getElementsByTagName("neighbor")
        neighbs = []
        for neigh in neighbors:
            neighbs.append(neigh.childNodes[0].data)
        ter = Territory(name, continent, None, neighbs)
        territories[name] = ter
        
    for terrs in territories.values():
        terrs.linkreferences()
        
    cont_structs = terr.getElementsByTagName("continent")
    for con in cont_structs:
        continents.append((con.getAttribute("name"), 
                           int(con.getAttribute("value"))))
    loadcards(terr)

def loadcards(xmlFile):
    """Load the data for the cards from the file."""
    global incrementval, cardvals, pictures
    cardvals = []
    pictures = []
    card = xmlFile.getElementsByTagName("cards")[0]
    for pic in card.getElementsByTagName("picture"):
        pictures.append(pic.childNodes[0].data)
    for cvalue in card.getElementsByTagName("card"):
        cardvals.append(int(cvalue.childNodes[0].data))
    incremtag = card.getElementsByTagName("increase")[0]
    incrementval = int(incremtag.childNodes[0].data)
    

      
class Card(object):
    """This just stores the information for one of the game's cards."""
    def __init__(self, territory, picture):
        self.territory = territory
        self.picture = picture

allcards = []

def createcards():
    """Create the set of cards."""
    wildcard = "Wildcard"
    for terr in range(2):
        car = Card(territories.values()[terr].name, wildcard)
        allcards.append(car)
    for terr in range(2, len(territories)):
        car = Card(territories.values()[terr].name, random.choice(pictures))
        allcards.append(car)
    random.shuffle(allcards)


currentcard = 0
pictures = []
cardvals = []
incrementval = 0


class Player(object):
    """Represents a player."""
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.freeArmies = 0
        self.conqueredTerritory = 0
    def territories(self):
        """Returns a list of the territories this player owns."""
        return [x for x in territories.values() if x.player == self]
    def place_army(self, terr, number = 1):
        """Place this player's army"""
        if terr.player == None:
            terr.player = self
        if self.freeArmies >= number:
            terr.armies += number
            self.freeArmies -= number

def eqpics(a, b):
    """Check if two pictures are equal."""
    return a == b or a == "Wildcard" or b == "Wildcard"
    
def cardset(cards):
    """See if the given list of cards makes a set."""
    cards.sort(lambda a, b:cmp(a.picture, b.picture))
    
    if eqpics(cards[0].picture, cards[1].picture) and \
       eqpics(cards[1].picture, cards[2].picture):
        return 1
    else: 
        for card in range(len(cards)-1):
            if cards[card].picture == cards[card+1].picture and \
               cards[card].picture != "Wildcard":
                return 0
    return 1

def turnincards(player, cards):
    """Turn in a set of cards."""
    global currentcard
    if risknetwork.turnincards(cards):
        return
    
    if phase != "Place":
        return
        
    for c in cards:
        if not c in player.cards:
            return
            
    cards.sort(lambda a, b:cmp(a.picture, b.picture))
    
    if not cardset(cards):
        return
        
    for c in cards:
        if territories[c.territory].player == player:
            territories[c.territory].armies += 2
            riskgui.drawarmy(territories[c.territory])
        
    if currentcard < len(cardvals):
        player.freeArmies += cardvals[currentcard]
    else:
        player.freeArmies += cardvals[-1] + \
                             incrementval * (currentcard - len(cardvals) + 1)
    currentcard += 1
    
    
    for c in cards:
        allcards.append(c)
        for ca in player.cards:
            if c == ca:
                player.cards.remove(ca)
                risknetwork.remove_card(ca, currentplayer)
    riskgui.set_armies(currentplayer.freeArmies)  


def makeplayer(pl, aifile=None):
    """Set up a player."""
    risknetwork.newplayer(pl)
    p = Player(pl)
    players[pl] = p
    if aifile:
        gai = imp.new_module("ai")
        filecode = open(aifile)
        exec filecode in gai.__dict__
        filecode.close()
        p.ai = gai
        p.ainame = aifile
    else:
        p.ai = None
    return p


def removeplayer(player, conqueror):
    """Remove a dead player from the game."""
    global currentplayernum, playerorder
    for card in player.cards:
        risknetwork.add_card(card, conqueror)
        risknetwork.remove_card(card, player)
    conqueror.cards += player.cards
    if currentplayernum >= playerorder.index(player):
        currentplayernum -= 1
    riskgui.removeplayer(player.name)
    risknetwork.removeplayer(player.name)
    playerorder.remove(player)
    del players[player.name]
    
    if len(players) == 1: #game over
        riskgui.won_game(players.values()[0].name)
        setphase("PostGame")


phase = "Pregame"
selected = None
currentplayer = None
currentplayernum = 0
armiesfrom = None
armiesto = None
playerorder = []

def setphase(newphase):
    """Set the current plase of the game."""
    global phase
    risknetwork.set_phase(newphase)
    phase = newphase
    
def resetturn():
    """Start the next turn with the first player."""
    global currentplayernum
    currentplayernum = len(players) - 1
    nextturn()

def rotateplayers():
    """Set currentplayer to the next player."""
    global currentplayer, currentplayernum
    currentplayernum += 1
    if currentplayernum >= len(playerorder):
        currentplayernum = 0
    currentplayer = playerorder[currentplayernum]
    riskgui.playersturn(currentplayer.name)


def handle_preposition(terr, button):
    """Handle the preposition phase."""
    if currentplayer.freeArmies == 0:
        resetturn()
        return
    
    emptyTerritories = [x for x in territories.values() if x.armies == 0] 
    if (emptyTerritories and terr.player is None) or \
            (not emptyTerritories and terr.player == currentplayer):
        terr.player = currentplayer
        currentplayer.place_army(terr)
        riskgui.drawterritory(terr, 0)
    else:
        return

    rotateplayers()
    riskgui.set_armies(currentplayer.freeArmies)
    while currentplayer.ai is not None:
        currentplayer.ai.run_preplace(currentplayer)
        rotateplayers()
        riskgui.set_armies(currentplayer.freeArmies)
        if currentplayer.freeArmies == 0:
            resetturn()
            return
  
def handle_fortifying(terr, button):
    """Handle the fortification phase."""
    global armiesfrom, armiesto
    if terr.player != currentplayer:
        return
    if armiesfrom is not None and armiesto is not None and \
       (selected != armiesfrom or terr != armiesto):
        riskgui.set_status("You can only fortify from one place to one space per turn.")
        return
    if not selected.neighboring(terr):
        return
        
    moving = min(selected.armies - 1, (button == 3) and 5 or 1)
    if moving:
        selected.armies -= moving
        terr.armies += moving
        armiesfrom = selected
        armiesto = terr
        riskgui.drawterritory(armiesfrom, 1)
        riskgui.drawterritory(armiesto, 0)
  
def handle_attack(defender):
    """Handle the attack phase."""
    global armiesto, selected
    if defender.player == currentplayer:
        return
    attacker = selected
    attack(attacker, defender)

    if defender.player == currentplayer and attacker.armies > 1: #we won
        riskgui.set_status(currentplayer.name + " won the territory - move armies into it")
        armiesto = defender
        setphase("WonAttack")
        
    if defender.player == currentplayer and attacker.armies == 1:
        riskgui.set_status(currentplayer.name + " won the territory")
        riskgui.drawterritory(attacker, 0)
        selected = None
    else:
        riskgui.drawterritory(attacker, 1)
    riskgui.drawterritory(defender, 0)

def handle_won_attack(terr, button):
    """Handle the movement of armies after an attack was won."""
    global selected
    if terr == armiesto:
        if button == 3:
            moved = min(5, selected.armies - 1)
            selected.armies -= moved
            terr.armies += moved
        else:
            selected.armies -= 1
            terr.armies += 1
        riskgui.drawterritory(selected, 1)
        riskgui.drawterritory(terr, 0)
        if selected.armies == 1:
            setphase("Attack")
            riskgui.drawterritory(selected, 0)
            selected = None          
            return

def handle_place(terr, button):
    """Handle the placing of the armies before a turn."""
    if terr.player != currentplayer:
        return 1
    if currentplayer.freeArmies > 0:
        if button == 3:
            currentplayer.place_army(terr, min(5, currentplayer.freeArmies))
        else:
            currentplayer.place_army(terr)
        riskgui.drawarmy(terr)
        riskgui.set_armies(currentplayer.freeArmies)
        return 1
    else:
        if len(currentplayer.cards) >= 5:
            riskgui.set_status("You must turn in cards to attack")
            return 1
        riskgui.set_status("Moving to Attack")
        setphase("Attack")
        print >>verbosefile, "Attacking"
        return 0

    
def handleselection(t, button):
    """Handle a player clicking on the map."""
    global selected
    

    if phase == "Pregame":
        return
        
    if risknetwork.handle_selection(t, button):
        return
        
    if phase == "Preposition":
        handle_preposition(t, button)
        return
            
    if phase == "Place":
        if handle_place(t, button):
            return
            
    if selected is None:
        if t.player != currentplayer:
            return
        isshaded = 1
        selected = t
    elif selected == t:
        isshaded = 0
        selected = None
        if phase == "WonAttack":
            setphase("Attack")
    else:
        if phase == "Fortifying":
            handle_fortifying(t, button) 
        elif phase == "Attack":
            handle_attack(t)
        elif phase == "WonAttack":
            handle_won_attack(t, button)
        return
        
    riskgui.drawterritory(t, isshaded)  

def startfortifying():
    """Handle when the player wants to start fortifying."""
    global armiesfrom, armiesto, selected
    if risknetwork.start_fortifying():
        return
        
    if phase == "Pregame" or phase == "Preposition" or phase == "Fortifying" or (
                                 phase != "Attack" and 
                                 currentplayer.freeArmies > 0):
        riskgui.set_status("No can do")
        return
    if phase == "Place" and len(currentplayer.cards) >= 5:
        riskgui.set_status("You must turn in your cards to start fortifying.")
        return
    if selected is not None:
        riskgui.drawterritory(selected, 0)      
        selected = None
    setphase("Fortifying")
    riskgui.set_status("Now fortifying...")
    armiesfrom = None
    armiesto = None

    
def startgame():
    """Start off the game."""
    global playerorder, currentplayer
    if risknetwork.am_client:
        riskgui.show_status_message("You aren't the server; you can't do that.")
        return False
        
    if phase != "Pregame":
        return False
    if len(players) < 2:
        riskgui.set_status("Not enough players")
        return False
    if len(players) > 7:
        riskgui.set_status("Too many players - 7 maximum")
        return False
    
    
    setphase("Preposition")
    
    createcards()
    for pl in players.values():
        pl.freeArmies = 45 - 5 * len(players)
    playerorder = players.values()[:]
    random.shuffle(playerorder)
    currentplayer = playerorder[0]
    riskgui.relistplayers(playerorder)
    riskgui.playersturn(currentplayer.name)
    riskgui.set_armies(currentplayer.freeArmies)
    
    
    while currentplayer.ai is not None and currentplayer.freeArmies > 0:
        currentplayer.ai.run_preplace(currentplayer)
        rotateplayers()  
        riskgui.set_armies(currentplayer.freeArmies)
    if currentplayer.ai is not None:
        resetturn()
        nextturn()
    return True
    

def nextturn():
    """Move on to the next turn."""
    if phase == "Pregame":
        return
    if risknetwork.next_turn():
        return
    if currentplayer.freeArmies > 0:
        riskgui.set_status("You must position all your armies first")
        return
    real_nextturn()
    while currentplayer.ai is not None:
        if len(players) == 1:
            riskgui.set_status(currentplayer.name + " won!")
            return
        setphase("Place")
        currentplayer.ai.run_place(currentplayer)
        setphase("Attack")
        currentplayer.ai.run_attack(currentplayer)
        real_nextturn()
        
def real_nextturn():
    """Hidden method to really move on."""
    global phase, selected
    
    if selected is not None:
        riskgui.drawterritory(selected, 0)
        selected = None
    
    if currentplayer.conqueredTerritory == 1:
        if len(allcards) != 0: #too bad otherwise
            handcard = random.choice(allcards)
            currentplayer.cards.append(handcard)
            risknetwork.add_card(handcard, currentplayer)
            allcards.remove(handcard)
        currentplayer.conqueredTerritory = 0
        
    rotateplayers()
    riskgui.set_status("It is now " + currentplayer.name + "'s turn.")
    
    currentplayer.freeArmies += max(3, len(currentplayer.territories()) // 3)
    for c in continents:
        existing = [x for x in territories.values() if x.continent == c[0]]
        unowned = [x for x in existing if x.player != currentplayer]
        if len(existing) != 0 and len(unowned) == 0 :
            currentplayer.freeArmies += c[1]
    riskgui.set_armies(currentplayer.freeArmies)            
            
    setphase("Place")

def save_game(filename):
    """Save the game."""
    if phase == "Pregame":
        riskgui.set_status("You can't save, you haven't even started.")
        return
        
    savefile = open(filename,"w")
    for player in playerorder:
        savefile.write("player\n")
        savefile.write(player.name + "\n")
        savefile.write(str(player.freeArmies) + "\n")
        savefile.write(str(player.conqueredTerritory)  + "\n")
        for card in player.cards:
            savefile.write(card.territory + "\n")
            savefile.write(card.picture + "\n")
        if player.ai:
            savefile.write("ai\n")
            savefile.write(player.ainame + "\n")
            aidata = player.ai.saveddata()
            savefile.write(str(len(aidata))+"\n")
            savefile.write(aidata)
        savefile.write("endplayer\n")
    savefile.write("endplayers\n")
    savefile.write(currentplayer.name + "\n")
    savefile.write(phase + "\n")
    savefile.write(str(currentcard) + "\n")
    for territory in territories.values():
        savefile.write("territory\n")
        savefile.write(territory.name + "\n")
        if territory.player:
            savefile.write(territory.player.name + "\n")
        else:
            savefile.write("None\n")
        savefile.write(str(territory.armies) + "\n")
        savefile.write("endterritory\n")
    savefile.write("cards\n")
    for card in allcards:
        savefile.write(card.territory + "\n")
        savefile.write(card.picture + "\n")
    savefile.close()

def load_game(filename):
    """Load a previously-saved game."""
    global currentplayer, phase, currentcard, currentplayernum
    if phase != "Pregame":
        riskgui.set_status("You have already started a game")
        return
        
    savefile = open(filename)
    while savefile.readline() == "player\n":
        plname = savefile.readline().strip()
        plarmies = int(savefile.readline().strip())
        plconquered = int(savefile.readline().strip())
        cards = []
        currentline = savefile.readline()
        while currentline != "endplayer\n" and currentline != "ai\n":
            nline = savefile.readline().strip()
            cards.append(Card(currentline.strip(),nline))
            currentline = savefile.readline()
        ainame = None
        if currentline == "ai\n":
            ainame = savefile.readline().strip()
            aidatalen = int(savefile.readline().strip())
            aidata = savefile.read(aidatalen)
            savefile.readline()
        if not players.has_key(plname):
            if ainame and not os.path.exists(ainame):
                riskgui.set_status("AI " + ainame + " nonexistent")
                ainame = None
            riskgui.makeplayercolors(makeplayer(plname, ainame))
            if ainame:
                players[plname].ai.loaddata(aidata)
        players[plname].freeArmies = plarmies
        players[plname].conqueredTerritory = plconquered
        players[plname].cards = cards
        for card in cards:
            risknetwork.add_card(card, players[plname])
        playerorder.append(players[plname])
    riskgui.relistplayers(playerorder)
    currentplayer = players[savefile.readline().strip()]
    currentplayernum = playerorder.index(currentplayer)
    riskgui.set_armies(currentplayer.freeArmies)
    riskgui.playersturn(currentplayer.name)
    setphase(savefile.readline().strip())
    currentcard = int(savefile.readline().strip())
    
    while savefile.readline().strip() == "territory":
        tname = savefile.readline().strip()
        tplayer = savefile.readline().strip()
        if tplayer == "None":
            tplayer = None
        else:
            tplayer = players[tplayer]
        territories[tname].player = tplayer
        territories[tname].armies = int(savefile.readline().strip())
        riskgui.drawterritory(territories[tname], 0)
        savefile.readline()

    while 1:
        cardterr = savefile.readline().strip()
        if not cardterr:
            break
        allcards.append(Card(cardterr,savefile.readline().strip()))
    savefile.close()
    
    
        
    