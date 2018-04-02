""" This program uses an interesting method to divide between client and 
server.  The server runs like normal, and when there's a gui event a client
should know about, it sends a message to the appropriate client.  When the 
client presses a button or tries to select a territory, the command is 
simply sent to the server.  This causes some lag, but it makes the program
much simpler.  The client needs to know almost no game logic."""

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

import socket
import thread
import sys
import time

import riskengine
import riskgui

port = 32296

class StringSocket(socket.socket):
    """This class has a readline method to read lines at a time.  
       It works on nonblocking sockets.
       """
    def __init__(self, 
                 family=socket.AF_INET, 
                 type=socket.SOCK_STREAM, 
                 proto=0, 
                 _sock=None):
        socket.socket.__init__(self, family, type, proto,_sock) 
        self.line = ""
        self.fine = 1
    def readline(self):
        """Read a line from the socket"""
        if self.line.find("\n") > -1:
            outstr = self.line[:self.line.find("\n")]
            self.line = self.line[self.line.find("\n")+1:]
            return outstr
        try:
            self.line += self.recv(1024)
        except socket.error, (ErrorValue, ErrorTB):
            if ErrorValue != 10035 and ErrorValue != 11: #not portable, too bad
                raise 
            return None
            
        if self.line.find("\n") > -1:
            outstr = self.line[:self.line.find("\n")]
            self.line = self.line[self.line.find("\n")+1:]
            return outstr
        return None
    def accept(self):
        """Accept a socket"""
        sock, addr = self._sock.accept()
        return StringSocket(_sock=sock), addr
    def send(self, data):
        """Send some data"""
        if self.fine == 1:
            try:
                socket.socket.send(self, data)
            except socket.error, (ErrorValue, ErrorTB):
                self.fine = 0
                riskgui.set_status("Connection broken.")
                



sockets = []
serv_sock = None
am_server = 0
am_client = 0

def handle_network():
    """Repeatedly handle input from the network"""
    global line
    if am_server:
        for s in sockets:
            while 1:
                lin = None
                try:
                    lin = s.readline()
                except:
                    (ErrorType, ErrorValue, ErrorTB)=sys.exc_info()
                    riskgui.set_status("A client disconnected.")
                if lin:
                    server_receive_message(lin, s)
                else:
                    break
    if am_client:
        while 1:
            lin = None
            try:
                lin = serv_sock.readline()
            except:
                (ErrorType, ErrorValue, ErrorTB)=sys.exc_info()
                riskgui.set_status("Connection broken.")
                return
            if lin:
                client_receive_message(lin, serv_sock)
            else:
                break  
    riskgui.root.after(50, handle_network)



def start_server():
    """Start up the server"""
    global serv_sock, am_server
    if am_server == 1:
        riskgui.set_status("Server already started.")
        return
    am_server = 1
    serv_sock = StringSocket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.bind(('', port))
    thread.start_new_thread(binder,())
    try:
        riskgui.set_status("My IP: "+ socket.gethostbyname(socket.getfqdn('')))
        return
    except:
        pass
    try:
        riskgui.set_status("My IP: "+ socket.gethostbyname(socket.gethostname()))
        return
    except:
        pass  
    
def binder():
    """Get connections to the server"""
    serv_sock.listen(1)
    while 1:
        q, v = serv_sock.accept()
        q.setblocking(0)        
        sockets.append(q)
        riskgui.set_status("Got connection")
     
def start_client(host):
    """Start up the client"""
    global serv_sock, am_client
    if am_client:
        riskgui.set_status("Already connected to a server.")
        return
        
    try:
        serv_sock = StringSocket(socket.AF_INET, socket.SOCK_STREAM)
        serv_sock.connect((socket.gethostbyname(host), port))
        serv_sock.setblocking(0)
    except:
        riskgui.set_status("Unable to connect to server.")
        return
    am_client = 1
    riskgui.set_status("Connected to server.")

def sockettoplayer(sock):
    """This takes a socket and outputs a player (not necessarily the one we want)."""
    #first check if the current player is on this socket
    if hasattr(riskengine.currentplayer, "connection") and riskengine.currentplayer.connection == sock:
        return riskengine.currentplayer
    #second check if any player is on this socket
    for pl in riskengine.players.values():
        if hasattr(pl, "connection") and not pl.ai and pl.connection == sock:
            return pl
    #just an observer
    return None
    
def sendparts(sck, *parts):
    """Send the combined parts of the message to the specified socket"""
    try:
        sck.send(" ".join(str(a).replace("-","-0").replace(" ","-1").replace("\n","-2") for a in parts) + "\n")
    except socket.error, (ErrorValue, ErrorTB):
        if ErrorValue == 10035:
            time.sleep(1)
            sendparts(sck, *parts)
        else:
            riskgui.set_status("Connection broken.")
            raise

def sendall(*parts):
    """Send the combined parts of the message to every socket (from the server)"""
    for sock in sockets:
        sendparts(sock, *parts)

def clientsend(*parts):
    """Send the combined parts of the message to the server if we are the client.
    Return 1 if we sent, 0 if we didn't"""
    if am_client:
        sendparts(serv_sock, *parts)
        return 1
    return 0

def playersend(pl, *parts):
    """Send the combined parts of the message to the player (if we're the server)."""
    if am_server:
        if hasattr(pl, "connection"):
            sendparts(pl.connection, *parts)        

def handle_selection(t, button):
    """This is called when a player selects a territory"""
    return clientsend('handle_selection', t.name, button)

def draw_army(t):
    sendall("draw_army", t.name, t.armies, t.player and t.player.name)

def draw_territory(t, isselected):
    sendall('draw_territory', t.name, t.armies, t.player and t.player.name, isselected)

def set_armies(pl):
    playersend(pl, "set_armies", pl and pl.freeArmies)

def won_game(pl):
    sendall("won_game", pl)

def playersturn(pl): 
    sendall("playersturn", pl)

def set_status(string):
    sendall("set_status" + string)

def newplayer(plname):
    if am_server:
        riskgui.set_status("New player " + plname) 
        sendall("newplayer", plname)
    clientsend("newplayer", plname)
        
def removeplayer(plname):
    sendall("removeplayer", plname)
        
def relistplayers(pllist):
    sendall("relistplayers", *[p.name for p in pllist])
        
def turnincards(cards):
    return clientsend("turnincards", *[c.territory for c in cards])

def set_phase(phase):
    sendall("set_phase", phase)

def start_fortifying():
    return clientsend("start_fortifying")

def next_turn():
    return clientsend("next_turn")
    
def add_card(card, player):
    playersend(player, 'add_card', card.picture, card.territory, player.name)
            
def remove_card(card, player):
    playersend(player, 'remove_card', card.picture, card.territory, player.name)

def leaving():
    if am_server:
        sendall("leaving")
    clientsend("leaving")
    
def sendmessage(message):
    if am_client:
        client_message(message)
    if am_server:
        server_message(message, None)

def client_message(message):
    clientsend("message", message)

def server_message(message, username):
    if username is None:
        if riskengine.currentplayer and not hasattr(riskengine.currentplayer,"connection"):
            username = riskengine.currentplayer.name
        else:
            for pl in riskengine.players.values():
                if not hasattr(pl, "connection") and not pl.ai:
                    username = pl.name
                    break
            if username is None:
                username = "Master"
    
    sendall("message", message, username)
    riskgui.show_status_message(username + ": " + message) 
  
def splitparms(s):
    """Split a string into parts, decoding parts"""
    return [st.replace("-1"," ").replace("-2","\n").replace("-0", "-") for st in s.split(" ")]

  
  
def client_receive_message(mess, sock):
    """Run when the client receives a message."""
    global clplayer, am_client
    print >>riskengine.verbosefile, mess, "client received"
    parts = splitparms(mess)
    if parts[0] == "draw_army" or parts[0] == "draw_territory":
        terr = riskengine.territories[parts[1]]
        terr.armies = int(parts[2])
        terr.player = riskengine.players[parts[3]]
        if parts[0] == "draw_army":
            riskgui.drawarmy(terr)
        else:
            riskgui.drawterritory(terr, int(parts[4]))
    if parts[0] == "set_armies":
        riskgui.set_armies(int(parts[1]))
    if parts[0] == "won_game":
        riskgui.won_game(parts[1])
    if parts[0] == "playersturn":
        riskgui.playersturn(parts[1])
    if parts[0] == "set_status":
        riskgui.set_status(parts[1])
    if parts[0] == "newplayer":
        riskgui.net_newplayer(parts[1])
    if parts[0] == "removeplayer":
        riskgui.removeplayer(parts[1])   
    if parts[0] == "relistplayers":
        riskgui.relistplayers([riskengine.players[p] for p in parts[1:]])
    if parts[0] == "set_phase":
        riskengine.setphase(parts[1])
    if parts[0] == "add_card":
        riskengine.players[parts[3]].cards.append(riskengine.Card(parts[2], parts[1]))
    if parts[0] == "remove_card":
        foundcard = 0
        for n in riskengine.players[parts[3]].cards:
            if n.territory == parts[2]:
                riskengine.players[parts[3]].cards.remove(n)
                foundcard = 1
                break
        if foundcard == 0:
            print >>riskengine.verbosefile, "Couldn't find card"
            print >>riskengine.verbosefile, "players' cards:", riskengine.players[parts[3]].cards
        #riskengine.players[parts[3]].cards.remove(riskengine.card(parts[2], parts[1]))
    if parts[0] == "message":
        riskgui.set_status(parts[2] + " sent message: " + parts[1])
    if parts[0] == "leaving":
        riskgui.show_status_message("The server has left.")
        serv_sock.close()
        am_client = 0
        

def server_receive_message(mess, sock):
    """Run when the server receives a message"""
    print >>riskengine.verbosefile, mess, "server received"
    parts = splitparms(mess)
    if parts[0] == "newplayer":
        riskgui.net_newplayer(parts[1])
        riskengine.players[parts[1]].connection = sock
        for sck in sockets:
            if sck != sock:
                sendparts(sck, "newplayer", parts[1])
    if parts[0] == "handle_selection":
        if hasattr(riskengine.currentplayer, "connection") and riskengine.currentplayer.connection == sock:
            riskengine.handleselection(riskengine.territories[parts[1]], int(parts[2]))
    if parts[0] == "start_fortifying":
        riskengine.startfortifying()
    if parts[0] == "next_turn":
        riskengine.nextturn()
    if parts[0] == "turnincards":
        if hasattr(riskengine.currentplayer, "connection") and riskengine.currentplayer.connection == sock:
            cd = []
            for c in riskengine.currentplayer.cards:
                if c.territory in parts[1:]:
                    cd.append(c)
            riskengine.turnincards(riskengine.currentplayer, cd)
    if parts[0] == "message":
        pla = sockettoplayer(sock)
        if pla:
           plname = pla.name
        else:
           plname = "Someone"
        riskgui.set_status(plname + " sent message: " + parts[1])
    if parts[0] == "leaving":
        sockets.remove(sock)
        sock.close()
        pla = sockettoplayer(sock)
        if pla:
           plname = pla.name
        else:
           plname = "Someone"
        riskgui.set_status(plname + " has left")
            
