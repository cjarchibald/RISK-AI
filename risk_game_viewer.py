"""
This displays RISK game logs so that the games can be viewed
It was modified from the RISK.pyw program included in this assignment 
which was written by John Bauman
"""

from PIL import Image
from PIL import ImageDraw
from PIL import ImageTk
import tkinter as tk
import xml.dom.minidom
import random
import io
import zipfile
import gc
import sys

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
        self.pframe = tk.Frame(master, **kwargs)
        self.pack = self.pframe.pack
        self.statlabel = tk.Label(self.pframe)
        self.statlabel.pack(fill=tk.X)
        self.statlabel2 = tk.Label(self.pframe)
        self.statlabel2.pack(fill=tk.X)
        
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
        self.listframe = tk.Frame(master, **kwargs)
        self.pack = self.listframe.pack
        self.pstats = []
        
    def append(self, player):
        """Append a player to this list."""
        newpstat = PlayerStats(self.listframe)
        newpstat.pack()
        newpstat.set_id(player.id)
        self.pstats.append(newpstat)
        self.pack(fill=tk.X)
        
    def updateList(self, state):
        for p in state.players:
            for ps in self.pstats:
                if p.id == ps.id:
                    ps.update_stats(p, state)
        
            
class StatBoard:
    """Displays stats about current state"""
    def __init__(self, master, **kwargs):
        """Initialize it."""
        self.statframe = tk.Frame(master, **kwargs)
        self.pack = self.statframe.pack
        self.pstats = PlayerList(self.statframe)
        self.pstats.pack(fill=tk.X)
        self.sep3 = tk.Frame(self.statframe,height=1,width=50,bg="black") 
        self.sep3.pack(fill=tk.X)
        self.curturnnum = tk.Label(self.statframe, text="Turn Number: ")
        self.curturnnum.pack(fill=tk.X)
        self.curturnin = tk.Label(self.statframe, text="Next Card Turn-in Value: ")
        self.curturnin.pack(fill=tk.X)
        self.sep1 = tk.Frame(self.statframe,height=1,width=50,bg="black") 
        self.sep1.pack(fill=tk.X)
        self.curplayer = tk.Label(self.statframe, text="Current Player:")
        self.curplayer.pack(fill=tk.X)
        self.turntype = tk.Label(self.statframe, text="Turn Type:")
        self.turntype.pack(fill=tk.X)
        self.sep1 = tk.Frame(self.statframe,height=1,width=50,bg="black") 
        self.sep1.pack(fill=tk.X)
        self.lastplayer = tk.Label(self.statframe, text="Last Player:")
        self.lastplayer.pack(fill=tk.X)

        self.action = tk.Label(self.statframe, text="Last Action:")
        self.action.pack(fill=tk.X)
        self.sep2 = tk.Frame(self.statframe,height=1,width=50,bg="black") 
        self.sep2.pack(fill=tk.X)
        
    def add_player(self, player):
        """Add a player to the statBoard"""
        self.pstats.append(player)
        self.pack()
        
    def update_statBoard(self, state, last_action, last_player):
        """Update the players on the statBoard"""
        self.pstats.updateList(state)
        self.curturnnum.configure(text="Turn # " + str(turn_number) + " - State # " + str(state_number))
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
    stif = io.BytesIO(zfile.read(fname))
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
    ti = int(lv/3)
    return (int(value[0:ti],16), int(value[ti:2*ti],16), int(value[2*ti:lv],16), 255) 
                           
                           
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
    canvas.create_image(terr.x, terr.y, anchor=tk.NW, 
                            image=terr.currentimage, tags=(terr.name,))  
    drawarmy(t, 1)

           
#make 7 possible colors - should be enough for anyone        
possiblecolors = [(0,0,128),(128,0,0),(128,0,128),(0,128,0),(255,128,0),(0,128,255), (255,0,0), (0,255,255)]

def makeplayercolors(player):
    """Make the colors for a player"""
    colo = possiblecolors[0]
    possiblecolors.remove(colo)
    col = colo[0] * 2**16 + colo[1] * 2**8 + colo[2]
    
    back = 2**24-1
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
    global current_state
    if playing:
        nextstate()
    #delay = 500
    delay = 50
    #if current_state.turn_type == 'Place' or current_state.turn_type == 'PrePlace':
    if current_state.turn_type == 'Place':
        num_free = current_state.players[current_state.current_player].free_armies 
        if num_free > 3:
            delay = 50
        elif num_free > 1:
            delay = 250
        
    root.after(delay, play_log)
      
def setupdata():
    """Start the game"""
    global territories, canvas, root, gameMenu, playerMenu
    global totim, zfile, statbrd, play_button
    
    root = tk.Tk()
    root.title("PyRiskGameViewer")
    
    zfile = zipfile.ZipFile("world.zip")
    graphics = xml.dom.minidom.parseString(zfile.read("territory_graphics.xml"))
    loadterritorygraphics(graphics)   
    
    totalframe = tk.Frame(root)
    lframe = tk.Frame(totalframe)
    statbrd = StatBoard(lframe, bd=2)
    statbrd.pack(anchor=tk.N, fill=tk.Y, expand=tk.NO)
    tk.Button(lframe, text="Next State", 
                   command = nextstate).pack(padx=15,pady=15)
    lframe.pack(side=tk.LEFT, anchor=tk.S, fill=tk.Y)
    play_button = tk.Button(lframe, text="Play", command = toggle_playing)
    play_button.pack(padx=15,pady=15)
    lframe.pack(side=tk.LEFT, anchor=tk.S, fill=tk.Y)
   
    canvas = tk.Canvas(totalframe, 
                            height=graphics.childNodes[0].getAttribute("height"), 
                            width=graphics.childNodes[0].getAttribute("width"))

    boardname = graphics.getElementsByTagName("board")[0].childNodes[0].data
    total = opengraphic(boardname)
    totim = ImageTk.PhotoImage(total)
    canvas.create_image(0, 0, anchor=tk.NW, image=totim, tags=("bgr",))
    for terr in range(len(riskboard.territories)):
        drawterritory(terr, 0)
    
    del total
    
    canvas.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)    
    totalframe.pack(expand=tk.YES, fill=tk.BOTH)#set up message area
    
    gc.collect()
    
    play_log()
    
logfile = None
current_state = None
riskboard = None
turn_number = 0
state_number = 0

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
                drawterritory(tidx, (255,255,0, 255))
            if t is not None:
                tidx = current_state.board.territory_to_id[t]
                drawarmy(tidx)
            
    #Redraw the old territories normal again
    if previous_action and previous_action.type != 'TurnInCards':
        for t in prev_t:
            if t is not None and t not in changed_t:
                tidx = current_state.board.territory_to_id[t]
                drawterritory(tidx)

    if previous_action and previous_action.type == 'TurnInCards':
        # toggle_playing()
        # print("TURNED IN CARDS!!!")
        for i in [previous_action.to_territory, previous_action.from_territory, previous_action.troops]:
            if i is not None:
                t = current_state.board.cards[i].territory
                drawterritory(t)  #Cards store territory id

            
def nextstate(read_action=True):
    global current_state, logover, previous_action, previous_player, playing, turn_number, state_number

    if logover:
        print('LOG IS OVER NOW!')
        statbrd.log_over()
        playing = False
        return
    last_action = risktools.RiskAction(None,None,None,None)
    if logfile is not None:
        if read_action:
            newline = logfile.readline()
            splitline = newline.split('|')
            if not newline or splitline[0] == 'RISKRESULT':
                print('We have reached the end of the logfile')
                print(newline)
                logover = True
            else:
                last_action.from_string(newline) #This gets next action
        if not logover:
            current_state.from_string(logfile.readline(),riskboard)
    if not logover:
#        print("CURRENT STATE THAT IS BEING DISPLAYED:")
#        current_state.print_state()
        display_current_state(last_action)
    previous_action = last_action
    if current_state.current_player != previous_player:
        turn_number += 1
    state_number += 1
    previous_player = current_state.current_player

    if not logover and current_state.turn_type == 'GameOver':
        logover = True
        if logfile is not None:
            newline = logfile.readline()
            print('GAME OVER:  RESULT:')
            print(newline)
        
previous_action = None        
logover = False
previous_player = None
    
if __name__ == "__main__":
    #Set things up then call root.mainloop
    if len(sys.argv) < 2:
        print('Requires logfile!')
        sys.exit()

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