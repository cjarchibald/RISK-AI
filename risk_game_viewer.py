"""This does the graphics work for the program."""

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

from PIL import Image
from PIL import ImageDraw
from PIL import ImageTk
from PIL import PngImagePlugin #for py2exe
import Tkinter
import tkSimpleDialog
import tkFileDialog
import tkMessageBox
import xml.dom.minidom
import random
import cStringIO as StringIO
import zipfile
import gc
import sys
import time
Image._initialized = 1 #for py2exe

#import Tix

import risktools

territories = {}

canvas = None
root = None
totim = None
zfile = None
statbrd = None

class Territory:
    """Contains the graphics info for a territory"""
    def __init__(self, name, x, y, w, h, cx, cy):
        self.name = str(name)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cx = cx
        self.cy = cy

class PlayerStats:
    """This is used to display the stats for a single player"""
    def __init__(self, master, **kwargs):
        self.pframe = Tkinter.Frame(master, **kwargs)
        self.pack = self.pframe.pack
        self.statlabel = Tkinter.Label(self.pframe)
        self.statlabel.pack(fill=Tkinter.X)
        self.statlabel2 = Tkinter.Label(self.pframe)
        self.statlabel2.pack(fill=Tkinter.X)

    def set_id(self, id):
        self.id = id

    def update_stats(self, player, state):
        """Update the player stats"""
        num_armies = 0
        num_territories = 0
        for i in range(len(state.owners)):
            if state.owners[i] == player.id:
                num_territories += 1
                num_armies += state.armies[i]

        self.statlabel.configure(text=player.name + " : " + str(num_armies) + " in " + str(num_territories) + " territories. " + str(player.free_armies) + " free", fg=playercolors[player.id], bg=backcolors[player.id])

        #Make card string of first letters of card pictures
        cardstring = ""
        for c in player.cards:
            if len(cardstring) > 0:
                cardstring = cardstring + ","
            cardstring = cardstring + str(state.board.cards[c].picture)[0]

        self.statlabel2.configure(text="Cur Reinf: " + str(risktools.getReinforcementNum(state,player.id)) + " | Cards : " + cardstring, fg=playercolors[player.id], bg=backcolors[player.id])
        self.pack()

class PlayerList:
    """Actually lists the players."""
    def __init__(self, master, **kwargs):
        """Actually initialize it."""
        self.listframe = Tkinter.Frame(master, **kwargs)
        self.pack = self.listframe.pack
        self.pstats = []

    def append(self, player):
        """Append a player to this list."""
        newpstat = PlayerStats(self.listframe)
        newpstat.pack()
        newpstat.set_id(player.id)
        self.pstats.append(newpstat)
        self.pack(fill=Tkinter.X)

    def updateList(self, state):
        for p in state.players:
            for ps in self.pstats:
                if p.id == ps.id:
                    ps.update_stats(p, state)


class StatBoard:
    """Displays stats about current state"""
    def __init__(self, master, **kwargs):
        """Initialize it."""
        self.statframe = Tkinter.Frame(master, **kwargs)
        self.pack = self.statframe.pack
        self.pstats = PlayerList(self.statframe)
        self.pstats.pack(fill=Tkinter.X)
        self.sep3 = Tkinter.Frame(self.statframe,height=1,width=50,bg="black")
        self.sep3.pack(fill=Tkinter.X)
        self.curturnnum = Tkinter.Label(self.statframe, text="Turn Number: ")
        self.curturnnum.pack(fill=Tkinter.X)
        self.curturnin = Tkinter.Label(self.statframe, text="Next Card Turn-in Value: ")
        self.curturnin.pack(fill=Tkinter.X)
        self.sep1 = Tkinter.Frame(self.statframe,height=1,width=50,bg="black")
        self.sep1.pack(fill=Tkinter.X)
        self.curplayer = Tkinter.Label(self.statframe, text="Current Player:")
        self.curplayer.pack(fill=Tkinter.X)
        self.turntype = Tkinter.Label(self.statframe, text="Turn Type:")
        self.turntype.pack(fill=Tkinter.X)
        self.sep1 = Tkinter.Frame(self.statframe,height=1,width=50,bg="black")
        self.sep1.pack(fill=Tkinter.X)
        self.lastplayer = Tkinter.Label(self.statframe, text="Last Player:")
        self.lastplayer.pack(fill=Tkinter.X)

        self.action = Tkinter.Label(self.statframe, text="Last Action:")
        self.action.pack(fill=Tkinter.X)
        self.sep2 = Tkinter.Frame(self.statframe,height=1,width=50,bg="black")
        self.sep2.pack(fill=Tkinter.X)

    def add_player(self, player):
        """Add a player to the statBoard"""
        self.pstats.append(player)
        self.pack()

    def update_statBoard(self, state, last_action, last_player):
        """Update the players on the statBoard"""
        self.pstats.updateList(state)
        self.curturnnum.configure(text="Turn Number: " + str(turn_number))
        self.curturnin.configure(text="Next Card Turn-in Value: " + str(risktools.getTurnInValue(state)))
        self.curplayer.configure(text="Current Player: " + state.players[state.current_player].name)
        if last_player is not None:
            self.lastplayer.configure(text="Last Player: " + state.players[last_player].name)
        self.turntype.configure(text="Turn Type: " + state.turn_type)
        self.action.configure(text="Last Action: " + last_action.description(True))

    def log_over(self):
        self.curplayer.configure(text="LOG FILE IS OVER!")

def opengraphic(fname):
    """Load an image from the specified zipfile."""
    stif = StringIO.StringIO(zfile.read(fname))
    im = Image.open(stif)
    im.load()
    stif.close()
    return im


def drawarmy(t, from_territory=0):
    """Draw a territory's army"""
    terr = territories[riskboard.territories[t].name]
    canvas.delete(terr.name + "-a")
    if current_state.owners[t] is not None:
        canvas.create_rectangle(terr.cx + terr.x - 7, terr.cy + terr.y - 7,
                                terr.cx + terr.x + 7, terr.cy + terr.y+ 7,
                                fill=backcolors[current_state.owners[t]],
                                tags=(terr.name + "-a",))
        canvas.create_text(terr.cx + terr.x, terr.cy + terr.y,
                           text=str(current_state.armies[t]), tags=(riskboard.territories[t].name + "-a",), fill=playercolors[current_state.owners[t]])
    else:
        canvas.create_text(terr.cx + terr.x, terr.cy + terr.y,
                           text=str(0), tags=(terr.name + "-a",))

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return (int(value[0:0+lv/3],16), int(value[lv/3:2*lv/3],16), int(value[2*lv/3:lv],16), 255)


def drawterritory(t, color=None):
    """Draw an entire territory (will draw in color provided, default is owning player's color)"""
    terr = territories[str(riskboard.territories[t].name)]

    #Create colored version of the image
    canvas.delete(terr.name)

    if len(backcolors) > 0 and current_state.owners[t] is not None:
        for fp in terr.floodpoints:
            if color:
                ImageDraw.floodfill(terr.photo, fp, color)
            else:
                ImageDraw.floodfill(terr.photo, fp, hex_to_rgb(backcolors[current_state.owners[t]]))

    terr.currentimage = ImageTk.PhotoImage(terr.photo)
    canvas.create_image(terr.x, terr.y, anchor=Tkinter.NW,
                            image=terr.currentimage, tags=(terr.name,))
    drawarmy(t, 1)


#make 7 possible colors - should be enough for anyone
possiblecolors = [(0,0,128),(128,0,0),(128,0,128),(0,128,0),(0,128,128),(128,128,0), (255,0,0), (0,255,255)]

def makeplayercolors(player):
    """Make the colors for a player"""
    colo = possiblecolors[0]
    possiblecolors.remove(colo)
    col = colo[0] * 2**16 + colo[1] * 2**8 + colo[2]

    back = 2**24-1 - col
    pc = hex(col)[2:]
    pc = "0" * (6 - len(pc)) + pc
    backcolors.append("#" + pc)
    pc = hex(back)[2:]
    pc = "0" * (6 - len(pc)) + pc
    playercolors.append("#" + pc)

playercolors = []
backcolors = []

def newplayer(p):
    """Create a new player"""
    makeplayercolors(p)
    statbrd.add_player(p)


def loadterritorygraphics(xmlFile):
    """Load graphics information/graphics from a file"""
    global territories
    territories = {}
    territoryStructure = xmlFile.getElementsByTagName("territory")
    for i in territoryStructure:
        tname = i.getAttribute("name")
        grafile = i.getElementsByTagName("file")[0].childNodes[0].data
        attributes = i.getElementsByTagName("attributes")[0]
        x = int(attributes.getAttribute("x"))
        y = int(attributes.getAttribute("y"))
        w = int(attributes.getAttribute("w"))
        h = int(attributes.getAttribute("h"))
        cx = int(attributes.getAttribute("cx"))
        cy = int(attributes.getAttribute("cy"))
        floodpoints = i.getElementsByTagName("floodpoint")
        fps = []
        for fp in floodpoints:
            fpx = int(fp.getAttribute("x"))
            fpy = int(fp.getAttribute("y"))
            fps.append((fpx,fpy))

        shaded = opengraphic(grafile)

        t = Territory(tname, x, y, w, h, cx, cy)
        t.photo = shaded
        t.shadedimage = ImageTk.PhotoImage(shaded)
        t.currentimage = ImageTk.PhotoImage(t.photo.point(lambda x:1.2*x))
        territories[tname] = t
        t.floodpoints = fps
        del shaded

playing = False

def toggle_playing():
    global playing, play_button
    if playing:
        playing = False
        play_button.config(text="Play")
    else:
        playing = True
        play_button.config(text="Pause")

play_button = None

def play_log():
    if playing:
        nextstate()
    root.after(500, play_log)

def setupdata():
    """Start the game"""
    global territories, canvas, root, gameMenu, playerMenu
    global totim, zfile, statbrd, play_button

    root = Tkinter.Tk()
    root.title("PyRiskGameViewer")

    zfile = zipfile.ZipFile("world.zip")
    graphics = xml.dom.minidom.parseString(zfile.read("territory_graphics.xml"))
    loadterritorygraphics(graphics)

    totalframe = Tkinter.Frame(root)
    lframe = Tkinter.Frame(totalframe)
    statbrd = StatBoard(lframe, bd=2)
    statbrd.pack(anchor=Tkinter.N, fill=Tkinter.Y, expand=Tkinter.NO)
    Tkinter.Button(lframe, text="Next State",
                   command = nextstate).pack(padx=15,pady=15)
    lframe.pack(side=Tkinter.LEFT, anchor=Tkinter.S, fill=Tkinter.Y)
    play_button = Tkinter.Button(lframe, text="Play", command = toggle_playing)
    play_button.pack(padx=15,pady=15)
    lframe.pack(side=Tkinter.LEFT, anchor=Tkinter.S, fill=Tkinter.Y)

    canvas = Tkinter.Canvas(totalframe,
                            height=graphics.childNodes[0].getAttribute("height"),
                            width=graphics.childNodes[0].getAttribute("width"))

    boardname = graphics.getElementsByTagName("board")[0].childNodes[0].data
    total = opengraphic(boardname)
    totim = ImageTk.PhotoImage(total)
    canvas.create_image(0, 0, anchor=Tkinter.NW, image=totim, tags=("bgr",))
    for terr in range(len(riskboard.territories)):
        drawterritory(terr, 0)

    del total

    canvas.pack(side=Tkinter.RIGHT, expand=Tkinter.YES, fill=Tkinter.BOTH)
    totalframe.pack(expand=Tkinter.YES, fill=Tkinter.BOTH)#set up message area

    gc.collect()

    play_log()

logfile = None
current_state = None
riskboard = None
turn_number = 0

def display_current_state(last_action):
    if len(backcolors) == 0:
        #Load players from current state
        for p in current_state.players:
            newplayer(p)

    #Update stats display
    statbrd.update_statBoard(current_state, last_action, previous_player)

    #Draw territories that might have changed
    changed_t = [last_action.to_territory, last_action.from_territory]
    prev_t = []

    if previous_action and previous_action.type != 'TurnInCards':
        prev_t = [previous_action.to_territory, previous_action.from_territory]
    if last_action.type != 'TurnInCards':
        for t in changed_t:
            if t is not None and t not in prev_t:
                tidx = current_state.board.territory_to_id[t]
                drawterritory(tidx, (255,255,0))
            if t is not None:
                tidx = current_state.board.territory_to_id[t]
                drawarmy(tidx)

    #Redraw the old territories normal again
    if previous_action and previous_action.type != 'TurnInCards':
        for t in prev_t:
            if t is not None and t not in changed_t:
                tidx = current_state.board.territory_to_id[t]
                drawterritory(tidx)


def nextstate(read_action=True):
    global current_state, logover, previous_action, previous_player, playing, turn_number
    logover = False

    if logover:
        print 'LOG IS OVER NOW!'
        statbrd.log_over()
        playing = False
        return
    last_action = risktools.RiskAction(None,None,None,None)
    if logfile is not None:
        if read_action:
            newline = logfile.readline()
            splitline = newline.split('|')
            if not newline or splitline[0] == 'RISKRESULT':
                print 'We have reached the end of the logfile'
                print newline
                logover = True
            else:
                last_action.from_string(newline) #This gets next action
        if not logover:
            current_state.from_string(logfile.readline(),riskboard)
    if not logover:
        display_current_state(last_action)
    previous_action = last_action
    if current_state.current_player != previous_player:
        turn_number += 1
    previous_player = current_state.current_player

    if not logover and current_state.turn_type == 'GameOver':
        logover = True
        if logfile is not None:
            newline = logfile.readline()
            print 'GAME OVER:  RESULT:'
            print newline

previous_action = None
logover = False
previous_player = None

if __name__ == "__main__":
    #Set things up then call root.mainloop
    logfile = open(sys.argv[1]) #This is passed in
    l1 = logfile.readline() #Board
    #Set up risk stuff
    riskboard = risktools.loadBoard('world.zip')
    current_state = risktools.getInitialState(riskboard)
    #Set up display stuff
    setupdata()
    #Call to get things started
    nextstate(False)
    root.mainloop()