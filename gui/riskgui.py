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
#import PngImagePlugin #for py2exe
import tkinter as tk
from tkinter import simpledialog as simpledialog
from tkinter import filedialog as filedialog
from tkinter import messagebox as messagebox

import xml.dom.minidom
import random
import io
import zipfile
import gc
Image._initialized = 1 #for py2exe

from . import riskengine
# import gui.riskengine as riskengine
# import gui.risknetwork

clplayer = ""
territories = {}

canvas = None
root = None
plist = None
statuswind = None
entrystr = None
armieslabel = None
totim = None
scrlbr = None

class Territory:
    """Contains the graphics info for a territory"""
    def __init__(self, name, x, y, w, h, cx, cy):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cx = cx
        self.cy = cy

class ColoredList:
    """This is used to create a list of the players' colors"""
    def __init__(self, master, **kwargs):
        """Sets up the internal canvas"""
        self.canvas = tk.Canvas(master, height=100, 
                                     width=14, background="#ffffff", 
                                     bd=0, highlightbackground="#ffffff")
        self.canvas.pack(fill=tk.Y, **kwargs)
        self.currentpos = 0
        self.itemlist = []
        
    def append(self, fgcolor, bgcolor):
        """Appends a colored element to the list"""
        self.canvas.create_rectangle(1, self.currentpos*14 + 1, 
                                     15, self.currentpos*14 + 15, 
                                     fill=bgcolor,
                                     outline=bgcolor,
                                     tags=(str(self.currentpos) + "p",))
        self.canvas.create_oval(5, self.currentpos*14 + 5, 
                                11, self.currentpos*14 + 11, 
                                fill=fgcolor, 
                                outline=fgcolor,
                                tags=(str(self.currentpos) + "p",))
        self.currentpos += 1
        self.itemlist.append((fgcolor, bgcolor))
        
    def delete(self, first, last=0):
        """Deletes elements from first to last from the list"""
        for i in range(self.currentpos):
            self.canvas.delete(str(i) + "p")
        if last == tk.END:
            last = len(self.itemlist) + 1
        if last == 0:
            last = first + 1
        newitems = [self.itemlist[x] for x in range(len(self.itemlist)) if x < first or x >= last]
        self.itemlist = []
        self.currentpos = 0
        for x in newitems:
            self.append(x[0], x[1])

class PlayerList:
    """Actually lists the players."""
    def __init__(self, master, **kwargs):
        """Actually initialize it."""
        self.listframe = tk.Frame(master, **kwargs)
        self.pack = self.listframe.pack
        self.playerlist = tk.Listbox(self.listframe, bd=0, 
                                          highlightbackground="#ffffff")
        self.playerlist.pack(side=tk.LEFT, anchor=tk.N, fill=tk.Y, 
                             expand=tk.YES)
        self.cllist = ColoredList(self.listframe, side=tk.RIGHT)
    def append(self, player):
        """Append a player to this list."""
        self.playerlist.insert(tk.END, player.name)
        self.cllist.append(player.playercolor, player.backcolor)
    def delete(self, first, last=-1):
        """Delete a player from this list."""
        if last == -1:
            self.playerlist.delete(first)
            self.cllist.delete(first)
        else:
            self.playerlist.delete(first, last)
            self.cllist.delete(first, last)
    def get(self, first, last=-1):
        """Get item strings from this list."""
        if last == -1:
            return self.playerlist.get(first)
        return self.playerlist.get(first, last)
    def select(self, location):
        """Clear the previous selection and select an item."""
        self.playerlist.selection_clear(0, tk.END)
        self.playerlist.selection_set(location)
            
def opengraphic(fname):
    """Load an image from the specified zipfile."""
    stif = io.BytesIO(riskengine.zfile.read(fname))
    im = Image.open(stif)
    im.load()
    stif.close()
    return im

def findterritory(x, y):
    """See which territory was selected at the given point"""
    for t in territories.values():
        if x >= t.x and y >= t.y and x < t.x + t.w and y < t.y + t.h:
            #we may have a winner - inside b-box
            pixel = t.photo.getpixel((x - t.x, y - t.y))
            if pixel[3] > 0:
                # this is it
                return t.name
    return None


def drawarmy(t, from_territory=0):
    """Draw a territory's army"""
    terr = territories[t.name]
    canvas.delete(t.name + "-a")
    if t.player:
        canvas.create_rectangle(terr.cx + terr.x - 7, terr.cy + terr.y - 7, 
                                terr.cx + terr.x + 7, terr.cy + terr.y+ 7, 
                                fill=t.player.backcolor, 
                                tags=(t.name + "-a",))
        canvas.create_text(terr.cx + terr.x, terr.cy + terr.y, 
                           text=str(t.armies), tags=(t.name + "-a",), 
                           fill=t.player.playercolor)
    else:
        canvas.create_text(terr.cx + terr.x, terr.cy + terr.y, 
                           text=str(t.armies), tags=(t.name + "-a",))

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    ti = int(lv/3)
    return (int(value[0:ti],16), int(value[ti:2*ti],16), int(value[2*ti:lv],16), 255) 
         
def drawterritory(t, shaded):
    """Draw an entire territory (possibly shaded)"""
    terr = territories[t.name]
    
    #Create colored version of the image
    canvas.delete(terr.name) 
    #print 'Drawing territory: ', t.name
    if hasattr(t.player, 'backcolor'):
        for fp in terr.floodpoints:
            #print 'Flood-filling', terr.name, ' territory'
            ImageDraw.floodfill(terr.photo, fp, hex_to_rgb(t.player.backcolor))

        #print 'Saving images'
        terr.shadedimage = ImageTk.PhotoImage(terr.photo.point(lambda x:x * 0))
        terr.currentimage = ImageTk.PhotoImage(terr.photo)
    if shaded:
        canvas.create_image(terr.x, terr.y, anchor=tk.NW, 
                            image=terr.shadedimage, tags=(terr.name,))
    else:
        canvas.create_image(terr.x, terr.y, anchor=tk.NW, 
                            image=terr.currentimage, tags=(terr.name,))  
    drawarmy(riskengine.territories[terr.name], 1)


def handleclick(event):
    """Run the events for a canvas click"""
    tname = findterritory(canvas.canvasx(event.x), canvas.canvasy(event.y))

    if tname is None:
        return

    #if this is a client, don't listen to commands
    if riskengine.currentplayer and \
       hasattr(riskengine.currentplayer,"connection"):
        return
    riskengine.handleselection(riskengine.territories[tname], event.num)

    
compnum = 1
class PlayerDialog(simpledialog.Dialog):
    """Dialog that lets the player choose a name/ai"""
    def body(self, master):
        """Set up the body of this dialog"""
        tk.Label(self, text="Player Name:").pack()
        
        self.pstr = tk.StringVar()
        self.pname = tk.Entry(self, textvariable=self.pstr)
        self.pname.pack()
        self.set_ai = tk.Button(self, text="Set AI", 
                                         command=self.setai)
        self.set_ai.pack()
        self.ai_filename = ""
        return self.pname
    def setai(self):
        """Callback to set the ai"""
        global compnum
        self.ai_filename = filedialog.askopenfilename(initialdir="ai",
                                          filetypes=[("Python files","py")])
        if self.pstr.get() == "":
            self.pstr.set("Computer " + str(compnum))
            compnum += 1
    def apply(self):
        """Set info when the ok button is clicked"""
        self.PlayerName = self.pstr.get()

#make 8 possible colors - should be enough for anyone        
possiblecolors = [(0,0,128),(128,0,0),(128,0,128),(0,128,0),(255,128,0),(0,128,255), (255,0,0), (0,255,255)]



def makeplayercolors(player):
    """Make the colors for a player"""
    colo = random.choice(possiblecolors)
    possiblecolors.remove(colo)
    col = colo[0] * 2**16 + colo[1] * 2**8 + colo[2]
    
    back = 2**24-1 - col
    pc = hex(col)[2:]
    pc = "0" * (6 - len(pc)) + pc
    player.playercolor = "#" + pc
    pc = hex(back)[2:]
    pc = "0" * (6 - len(pc)) + pc
    player.backcolor = "#" + pc


def newplayer():
    """Create a new player"""
    if riskengine.phase != "Pregame":
        return
    if len(riskengine.players) > 7:
        set_status("You can have at most 7 players.")
        
    pdialog = PlayerDialog(root, "Choose the player's name")
    if hasattr(pdialog,"PlayerName"):
        
        p = riskengine.makeplayer(pdialog.PlayerName, pdialog.ai_filename)

        makeplayercolors(p)
        plist.append(p)
        gameMenu.entryconfig(3)
        gameMenu.entryconfig(4)
        
    
def playersturn(playername):
    """Display which player's turn it is"""
    global clplayer
    clplayer = playername
    items = plist.get(0, tk.END)
    for i in range(len(items)):
        if items[i] == playername:
            plist.select(i)
            break
            
def relistplayers(pllist):
    """Relist the players in the GUI, in turn order"""
    plist.delete(0, tk.END)
    for player in pllist:
        plist.append(player)

def set_armies(armynum):
    """Display the number of free armies"""
    armieslabel.configure(text="Armies: " + str(armynum))
            
def removeplayer(playername):
    """Remove a player from the list"""
    items = plist.get(0, tk.END)
    for i in range(len(items)):
        if items[i] == playername:
            plist.delete(i)
            break

class CardsDialog(simpledialog.Dialog):
    """Display a list of cards, and be able to turn them in"""
    def body (self, master):
        """Set up the body of the dialog"""
        tk.Label(self, text="Cards:").pack()
        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE)
        if clplayer:
            riskengine.currentplayer = riskengine.players[clplayer]
        for card in riskengine.currentplayer.cards:
            self.listbox.insert(tk.END, 
                                card.territory + " - " + card.picture)
        self.listbox.pack(fill=tk.Y, expand=tk.YES)
    def apply(self):
        """Run when ok is selected"""
        self.selectcards = self.listbox.curselection()
        
def showcards():
    """Show a player's cards"""
    if riskengine.phase == "Pregame":
        return
    
    if riskengine.currentplayer and \
       hasattr(riskengine.currentplayer, "connection"):
        return #even server shouldn't be able to see another client's cards
        
    cdialog = CardsDialog(root, "Cards:")
    if hasattr(cdialog, "selectcards"):
        cards = cdialog.selectcards
        if len(cards) != 3:
            return
        givecards = []
        for card in cards:
            givecards.append(riskengine.currentplayer.cards[int(card)])
        riskengine.turnincards(riskengine.currentplayer, givecards)

class ConnectDlg(simpledialog.Dialog):
    """Let a player choose which address to connect to"""
    def body (self, master):
        """Display the body of this dialog"""
        tk.Label(self, text="Address:").pack()
        self.entry = tk.Entry(self)
        self.entry.insert(tk.END,"127.0.0.1")
        self.entry.pack()
        return self.entry
    def apply(self):
        """Run when this is ok'd"""
        self.ip = self.entry.get()
    
def startgame():
    if riskengine.startgame():
        playerMenu.entryconfigure(0, state=tk.DISABLED)
        
def set_status(string):
    """Set the status message"""
    show_status_message(string)
    
def show_status_message(string):
    """Display a status message on this client alone."""
    statuswind.insert(tk.END, string + "\n")
    statuswind.yview('moveto','1.0')
    
def won_game(player):
    """Display a message about who won the game"""
    messagebox.showinfo("Game Over", player + " won the game")
    
def handlemessage(e):
    """Handle the entry of a message"""
    if entrystr.get() == "":
        return
    entrystr.set("")


def showhelp():
    global helpwindow
    helpwindow = tk.Toplevel()
    t = tk.Text(helpwindow)
    disptext = open("README.txt").read()
    t.insert(tk.END, disptext)
    t.pack()
    but = tk.Button(helpwindow, text="Close Help", 
                   command=closehelp).pack(padx=5, pady=5)
    
def closehelp():
    helpwindow.destroy()
def save_game():
    """Save the game"""
    filen = filedialog.asksaveasfilename(filetypes=[("Save File","sav")])
    if filen:
        riskengine.save_game(filen)

def load_game():
    """Load a save game."""
    filen = filedialog.askopenfilename(filetypes=[("Save File","sav")])
    if filen:
        try:
            riskengine.load_game(filen)
        except:
            set_status("Invalid save file.")
            
def load_new_world():
    """Load a map game."""
    if riskengine.phase != "Pregame":
        set_status("You can only do that before the game starts.")
        return
    filen = filedialog.askopenfilename(filetypes=[("Map", "zip")])
    if filen:
        try:
            reloadterritories(filen)
        except:
            set_status("Invalid map file.")

def reloadterritories(newmapfile):
    """Reload the list of territories"""
    global totim
    riskengine.openworldfile(newmapfile)
    riskengine.loadterritories()
    
    canvas.delete("bgr")
    for n in territories.values():
        canvas.delete(n.name)
        canvas.delete(n.name + "-a")
        
    graphics = xml.dom.minidom.parseString(riskengine.zfile.read("territory_graphics.xml"))
    loadterritorygraphics(graphics)
    canvas.configure(height=graphics.childNodes[0].getAttribute("height"), 
                     width=graphics.childNodes[0].getAttribute("width"))
    boardname = graphics.getElementsByTagName("board")[0].childNodes[0].data
    total = opengraphic(boardname)
    totim = ImageTk.PhotoImage(total)
    canvas.create_image(0, 0, anchor=tk.NW, image=totim, tags=("bgr",))
    for terr in riskengine.territories.values():
        drawterritory(terr, 0)
    
    riskengine.closeworldfile()
                     
            
    
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
        #print 'For territory ', tname, ' floodpoints ', fps
        shaded = opengraphic(grafile)

        #shaded = image.point(lambda i: .75*i) #make a darker image for the shaded version
        t = Territory(tname, x, y, w, h, cx, cy)
        t.photo = shaded
        t.shadedimage = ImageTk.PhotoImage(shaded)
        t.currentimage = ImageTk.PhotoImage(t.photo.point(lambda x:1.2*x))
        territories[tname] = t
        t.floodpoints = fps
        del shaded

def setupdata():
    """Start the game"""
    global territories, canvas, root, statuswind, gameMenu, playerMenu
    global entrystr, armieslabel, totim, scrlbr, zfile, plist

    root = tk.Tk()
    root.title("PyRisk")
    
    graphics = xml.dom.minidom.parseString(riskengine.zfile.read("territory_graphics.xml"))
    loadterritorygraphics(graphics)
    

    menuBar = tk.Menu(root)
    root["menu"] = menuBar
    gameMenu = tk.Menu(menuBar, tearoff=0)
    gameMenu.add_command(label="Start Game", command=startgame)
    gameMenu.add_separator()
    gameMenu.add_command(label="Load a Map", command=load_new_world)
    gameMenu.add_separator()
    gameMenu.add_command(label="Save Game", command=save_game)
    gameMenu.add_command(label="Load Game", command=load_game)
    gameMenu.add_separator()
    gameMenu.add_command(label="Exit", command=lambda:root.destroy())
    playerMenu = tk.Menu(menuBar, tearoff=0)
    playerMenu.add_command(label="New Player", command=newplayer)
    playerMenu.add_separator()
    playerMenu.add_command(label="Next Turn", command=riskengine.nextturn)
    playerMenu.add_command(label="Show Cards", command=showcards)
    playerMenu.add_command(label="Fortify", 
                           command=riskengine.startfortifying)
    helpMenu = tk.Menu(menuBar, tearoff=0)
    helpMenu.add_command(label="Help text", command=showhelp)
    menuBar.add_cascade(label="Game", menu=gameMenu)    
    menuBar.add_cascade(label="Player", menu=playerMenu)
    menuBar.add_cascade(label="Help", menu=helpMenu)
    
    
    totalframe = tk.Frame(root)
    lframe = tk.Frame(totalframe)
    plist = PlayerList(lframe, bd=2, relief=tk.SUNKEN)
    plist.pack(anchor=tk.N, fill=tk.Y, expand=tk.YES)
    armieslabel = tk.Label(lframe, text="Armies:")
    armieslabel.pack()
    tk.Button(lframe, text="Next Turn", 
                   command = riskengine.nextturn).pack(padx=5, pady=5)
    tk.Button(lframe, text="Fortify", 
                   command = riskengine.startfortifying).pack(padx=5, pady=5)
    tk.Button(lframe, text="Next State", 
                   command = riskengine.nextturn).pack(padx=5,pady=5)
    lframe.pack(side=tk.LEFT, anchor=tk.N, fill=tk.Y)
    
    
    
    canvas = tk.Canvas(totalframe, 
                            height=graphics.childNodes[0].getAttribute("height"), 
                            width=graphics.childNodes[0].getAttribute("width"))

    boardname = graphics.getElementsByTagName("board")[0].childNodes[0].data
    total = opengraphic(boardname)
    totim = ImageTk.PhotoImage(total)
    canvas.create_image(0, 0, anchor=tk.NW, image=totim, tags=("bgr",))
    for terr in riskengine.territories.values():
        drawterritory(terr, 0)
    
    del total
    
    canvas.bind("<Button-1>", handleclick)
    canvas.bind("<Button-3>", handleclick)
    canvas.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)
    
    
    totalframe.pack(expand=tk.YES, fill=tk.BOTH)#set up message area
    statusframe = tk.Frame(root, bd=2, relief=tk.SUNKEN)
    statuswind = tk.Text(statusframe, bd=0, height=4)
    scrlbr = tk.Scrollbar(statusframe, orient=tk.VERTICAL)
    scrlbr["command"] = statuswind.yview
    statuswind["yscrollcommand"] = scrlbr.set
    scrlbr.pack(fill=tk.Y, side=tk.RIGHT)
    statuswind.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)
    statusframe.pack(fill=tk.BOTH, expand=tk.YES)
    
    entrystr = tk.StringVar()#set up message entry
    entrybar = tk.Entry(root, textvariable=entrystr)
    entrybar.pack(side=tk.BOTTOM, fill=tk.X)
    entrybar.bind("<Return>", handlemessage)

    riskengine.closeworldfile()
    
    gc.collect()
    
def rungame():
    root.mainloop()
