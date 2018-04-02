import riskgui
import riskengine
import random
import zipfile
import xml.dom.minidom
import math
import pickle
import json

#
#Code by Chris Archibald, Fall 2014
#archibald@cse.msstate.edu
#

class RiskBoard():
    """
    Stores all of the information about the current Risk game that doesn't change
    over the course of the game, things like:
        - Which territories make up the map
        - Which territories are connected to which
        - What the continents are and which territories they are composed of
        - What the sequence of card turn-in values is
        - What players are in the game
        - What pictures are on the cards 
        - What the set of all cards is
    """
    def __init__(self):
        """
        Initialize a Risk Board.
        All of the variables are initially empty.  
        They should be filled in through other function calls
        """
        # An array of RiskPlayer objects   
        self.players = []               
        # A dictionary which is indexed by player name
        # and stores the id number of that player
        self.player_to_id = dict()
        # A dictionary which is indexed by player id
        # and stores the player name of that player
        self.id_to_player = dict()
        
        # An array of RiskTerritory objects
        self.territories = []           
        # A dictionary which is indexed by territory name
        # and stores the id number of that territory
        self.territory_to_id = dict()
        
        # An array of RiskCard objects
        self.cards = []                 
        # A dictionary which is indexed by card name 
        # (territory name of pictured territory, or wildcard)
        # Stores the id of that card
        self.card_to_id = dict()
        # An array of string descriptions of the different card pictures
        self.pictures = []
        
        # A dictionary of RiskContinent objects
        # indexed by continent name, stores 
        # corresponding RiskContinent object
        self.continents = dict()        
        
        # An array of the card turn-in-values 
        # turn_in_values[i] should give the number of troops
        # received for the i-th card turn-in
        self.turn_in_values = []
        # A number specifying the incremental gain in received troops
        # for card turn-ins beyond the length of turn-in-values array
        self.increment_value = 0
        
        
    def from_string(self, s):
        """
        Load RiskBoard information from a string.  
        We assume the string was created by the to_string 
        function.
        """
        ss = s.split('|')
        #Players
        ssp = ss[1].split(';')
        for p in ssp:
            if len(p) > 0:
                np = RiskPlayer(None,None,None,None)
                np.from_string(p)
                self.add_player(np)
        #Territories
        sst = ss[2].split(';')
        for t in sst:
            if t:
                nt = RiskTerritory(None,None)
                nt.from_string(t)
                self.add_territory(nt)
        #Continents
        ssc = ss[3].split(';')
        for c in ssc:
            if c:
            
                nc = RiskContinent(None,None)
                nc.from_string(c)
                self.add_continent(nc)
        #Cards
        ssd = ss[4].split(';')
        for d in ssd:
            if d:
                nd = RiskCard(None,None,None)
                nd.from_string(d)
                self.add_card(nd)
        #Turn in values
        self.turn_in_values = json.loads(ss[5])
        #Increment value
        self.increment_value = json.loads(ss[6])
        #Pictures
        self.pictures = json.loads(ss[7])
    
    def to_string(self):
        """Save the current RiskBoard to a string.  This is used to save games."""
        output_string = 'RISKBOARD|'
        #Players
        for p in self.players:
            output_string = output_string + p.to_string()
            output_string = output_string + ';'
        output_string = output_string + '|'
        #Territories
        for t in self.territories:
            output_string = output_string + t.to_string()
            output_string = output_string + ';'
        output_string = output_string + '|'
        #Continents
        for n,c in self.continents.iteritems():
            output_string = output_string + c.to_string() + ';'
        output_string = output_string + '|'
        #Cards 
        for c in self.cards:
            output_string = output_string + c.to_string()
            output_string = output_string + ';'
        output_string = output_string + '|'
        #Turn In Values
        output_string = output_string + json.dumps(self.turn_in_values)
        output_string = output_string + '|'
        #Increment value
        output_string = output_string + json.dumps(self.increment_value)
        output_string = output_string + '|'
        #Pictures
        output_string = output_string + json.dumps(self.pictures)
        
        return output_string
        
        
    def shuffle_players(self):
        """Randomize the player order.  Make sure everything is right after that"""
        player_order = range(len(self.players))
        random.shuffle(player_order)
        
        shuffled_players = []
        player_counter = 0
        for i in player_order:
            p = self.players[i]
            p.id = player_counter
            shuffled_players.append(p)
            self.player_to_id[p.name] = p.id
            self.id_to_player[p.id] = p.name
            player_counter += 1
            
        self.players = shuffled_players
        
        
    def add_player(self, player):
        """
        Add a player object to the list of players.
        Modify player_to_id and id_to_player to include new player
        """
        self.players.append(player)
        self.player_to_id[player.name] = player.id
        self.id_to_player[player.id] = player.name
        
    def add_territory(self, territory):
        """
        Add a territory object to the list of territories.
        Modify territory_to_id to include new territory
        """
        self.territories.append(territory)
        self.territory_to_id[territory.name] = territory.id
        
    def add_card(self, card):
        """
        Add a card object to the list of cards
        Modify card_to_id to include the new card
        """
        self.cards.append(card)
        self.card_to_id[self.territories[card.territory].name] = card.id
        
    def shuffle_cards(self):
        """Randomly shuffle the array of cards and reassign the card ids to be consistent"""
        random.shuffle(self.cards)
        for i in range(len(self.cards)):
            self.cards[i].id = i
            self.card_to_id[self.territories[self.cards[i].territory].name] = i
        
    def add_continent(self, continent):
        """Add a continent object to the list of continents"""
        if continent.name not in self.continents:
            self.continents[continent.name] = continent
            
    def set_turn_in_values(self, tiv):
        """Set the array of turn-in values (for card turn-ins)"""
        self.turn_in_values = tiv
        
    def set_increment_value(self, iv):
        """Set the increment value for card turn-ins beyond the end of turn_in_values"""
        self.increment_value = iv
            
    def print_board(self):
        """Display the Risk Board to the output."""
        print 'RISK BOARD'
        #PRINT TERRITORIES BY CONTINENT
        print 'CONTINENTS'
        for c in self.continents.values():
            c.print_continent(self)
        
        #PRINT CARDS
        print 'CARDS'
        for c in self.cards:
            c.print_card(self)
            
        #PRINT PLAYERS
        print 'PLAYERS'
        for p in self.players:
            p.print_player(self)
            
class RiskTerritory():
    """Stores all of the information for a territory"""
    def __init__(self, name, id):
        # The name of the territory (a string)
        self.name = name
        # The id number of the territory (an integer)
        self.id = id
        # An list of the id numbers of all territories neighboring this one
        self.neighbors = []
    
    def add_neighbor(self, neighbor):
        """Add a neighbor id to the neighbor list"""
        self.neighbors.append(neighbor)
    
    def print_territory(self, board, indent=0):
        """Display information about this territory to the output"""
        for i in range(indent):
            print ' ',
        print '[', self.name, '] (', self.id, ')'
        for i in range(indent+2):
            print ' ',
        print 'Neighbors:'
        for n in self.neighbors:
            for i in range(indent+3):
                print ' ',
            print board.territories[n].name
    
    def to_string(self):
        """Save the current Territory information to a string"""
        s = json.dumps(self.name) + '&' + json.dumps(self.id) + '&' + json.dumps(self.neighbors) 
        return s
        
    def from_string(self, s):
        """Load information about this territory from a string"""
        ss = s.split('&')
        self.name = json.loads(ss[0])
        self.id = json.loads(ss[1])
        self.neighbors = json.loads(ss[2])
    
class RiskPlayer():
    """Stores all information about a player in the game"""
    def __init__(self, name, id, free_armies, conquered_territory):
        """Initializes the various components of this RiskPlayer object"""
        # The Player's name (string)
        self.name = name
        # The Player's id (integer)
        self.id = id
        # A list of card id numbers that this player holds (integers)
        self.cards = []
        # The number of armies this player has, waiting to be placed on the board
        self.free_armies = free_armies
        # A boolean stating whether or not this player conquered a territory on 
        # their current turn
        self.conquered_territory = conquered_territory
    
    def add_card(self, card):
        """Adds a card (card id number) to the player's list of card ids"""
        self.cards.append(card)
    
    def add_armies(self, n):
        """Adds a number of armies to the player's free_armies count"""
        self.free_armies += n
    
    def print_player(self, board, indent=0):
        """Displays information about this player to the output"""
        for i in range(indent):
            print ' ',
        print '<', self.name, '> (', self.free_armies, ' free armies )'
        for i in range(indent+2):
            print ' ',
        print 'Cards:'
        for c in self.cards:
            board.cards[c].print_card(board, indent+3)
        
    def copy_player(self):
        """Creates a copy of this player and returns it"""
        np = RiskPlayer(self.name, self.id, self.free_armies, self.conquered_territory)
        np.cards = self.cards[:]
        return np
        
    def to_string(self):
        """Saves this player to a string"""
        s = json.dumps(self.name) + '.' + json.dumps(self.id) + '.' + json.dumps(self.cards) + '.' + json.dumps(self.free_armies) + '.' + json.dumps(self.conquered_territory)
        return s
        
    def from_string(self, s):
        """Loads player information from a string"""
        ss = s.split('.')
        self.name = json.loads(ss[0])
        self.id = json.loads(ss[1])
        self.cards = json.loads(ss[2])
        self.free_armies = json.loads(ss[3])
        self.conquered_territory = json.loads(ss[4])
    
class RiskCard():
    """Stores all the information for a risk card"""
    def __init__(self, territory, picture, id):
        """Initializes card information"""
        # The territory id number of the territory pictured on the card
        self.territory = territory
        # The picture on the card
        self.picture = picture
        # The id number of this card
        self.id = id
    
    def print_card(self, board, indent=0):
        """Displays information about this card to the output"""
        for i in range(indent):
            print ' ',
        print board.territories[self.territory].name, ' : ', self.picture
        
    def to_string(self):
        """Saves card information to a string"""
        s = str(self.territory) + '.' + str(self.picture) + '.' + str(self.id)
        return s
        
    def from_string(self, s):
        """Loads card information from a string"""
        ss = s.split('.')
        self.territory = json.loads(ss[0])
        self.picture = json.loads(ss[1])
        self.id = json.loads(ss[2])
        
class RiskContinent():
    """Stores all information related to a continent"""
    def __init__(self, name, reward):
        """Initializes the continent information"""
        # The name of this continent (string)
        self.name = name
        # The reward for this continent 
        # This is the number of troops bonus that a player gets if the player 
        # owns all of the territories in this continent
        self.reward = reward
        # A list of the territory id numbers of the territories in this continent
        self.territories = []
    
    def add_territory(self, territory):
        """Adds a territory to this continent"""
        if territory not in self.territories:
            self.territories.append(territory)
    
    def print_continent(self,board,indent=0):
        """Displays information about continent to output"""
        for i in range(indent):
            print ' ',
        print '{', self.name, '} : ', self.reward
        for t in self.territories:
            board.territories[t].print_territory(board, indent+2)
    
    def to_string(self):
        """Save continent information to string"""
        s = json.dumps(self.name) + '&' + json.dumps(self.reward) + '&' + json.dumps(self.territories)
        return s
    
    def from_string(self, s):
        """Load continent information from string"""
        ss = s.split('&')
        self.name = json.loads(ss[0])
        self.reward = json.loads(ss[1])
        self.territories = json.loads(ss[2])
    
def nextPlayer(state):
    """
    Moves the state's current_player to the next player in the order
    Also ensures that when it exits, the new state.current_player is still in the game
    Input: RiskState object
    """
    incrementPlayer(state)
    while state.current_player not in state.owners and None not in state.owners:
        incrementPlayer(state)
    
def incrementPlayer(state):
    """
    Increments the current_player of the input state
    Input: RiskState object
    """
    state.current_player = state.current_player + 1
    if state.current_player >= len(state.players):
        state.current_player = 0
    
class RiskState():
    """Stores all the information about a state of a Risk game"""
    
    def __init__(self, players, armies, owners, current_player, turn_type, turn_in_number, last_attacker, last_defender, cards, board):
        """Initializes a RiskState object"""
    
        # An array of RiskPlayer objects (the players in the game)
        self.players = players
        
        # An array of integers, indexed by territory id number, that 
        # stores the number of armies on that territory
        self.armies = armies
        
        # An array of integers, indexed by territory id number, that 
        # stores the player id number of the player who owns that territory
        self.owners = owners
        
        # The player id number of the current player (player whose turn it is)
        self.current_player = current_player
        
        # What kind of turn is it currently 
        # Choices = (PreAssign, PrePlace, Place, TurnInCards, Attack
        # Occupy, Fortify, GameOver)
        self.turn_type = turn_type
        
        # A list of all the card id numbers of the cards still in the deck
        self.cards = cards
        
        # How many card sets have been turned in?
        self.turn_in_number = turn_in_number
        
        # What is the territory id of the last territory that was attacking/defending 
        # Important to determine troop movements after territory is conquered
        self.last_attacker = last_attacker
        self.last_defender = last_defender
        
        # A RiskBoard object that stores all the non-changing information about
        # this risk game
        self.board = board
        
    def to_string(self):
        """Saves this state to a string"""
        s = 'RISKSTATE|'
        #players
        for p in self.players:
            s = s + p.to_string()
            s = s + ';'
        s = s + '|' + json.dumps(self.armies) + '|' + json.dumps(self.owners) + '|'
        s = s + json.dumps(self.current_player) + '|' + json.dumps(self.turn_type) + '|'
        s = s + json.dumps(self.cards) + '|' + json.dumps(self.turn_in_number) + '|'
        s = s + json.dumps(self.last_attacker) + '|' + json.dumps(self.last_defender)
        return s
        
    def from_string(self, s, board):
        """Loads this state from a string"""
        ss = s.split('|')
        if ss[0] != 'RISKSTATE':
            print 'THIS IS AN INVALID RISKSTATE'
        ps = ss[1].split(';')
        self.players = []
        for p in ps:
            if p:#len(p) > 0:
                np = RiskPlayer(None, None, None, None)
                np.from_string(p)
                self.players.append(np)
                
        self.armies = json.loads(ss[2])
        self.owners = json.loads(ss[3])
        self.current_player = json.loads(ss[4])
        self.turn_type = json.loads(ss[5])
        self.cards = json.loads(ss[6])
        self.turn_in_number = json.loads(ss[7])
        self.last_attacker = json.loads(ss[8])
        self.last_defender = json.loads(ss[9])
        self.board = board
        
    def print_state(self):
        """Displays information about this state to the output"""
        print 'PLAYERS'
        for p in self.players:
            p.print_player(self.board)
        
        print 'OWNERS/ARMIES'
        for i in range(len(self.armies)):
            if self.owners[i] in self.board.id_to_player:
                print self.board.territories[i].name, '[', self.board.id_to_player[self.owners[i]], '] : ', self.armies[i]
            else:
                print self.board.territories[i].name, '[', self.owners[i], '] : ', self.armies[i]
        
        if self.current_player < len(self.board.players):
            print 'CURRENT PLAYER: ', self.board.players[self.current_player].name, '[', self.current_player, ']'
        else:
            print 'CURRENT PLAYER: ??? [', self.current_player, ']'
        print len(self.cards), ' CARDS LEFT'
        
    def copy_state(self):
        """
        Creates a (deep) copy of this state and return it. Modifications to new state won't change original, except for the risk board, of which there is only one (it shouldn't be modified!)
        """
        copy_players = []
        for p in self.players:
            copy_players.append(p.copy_player())
        return RiskState(copy_players,self.armies[:],self.owners[:],self.current_player,self.turn_type,self.turn_in_number, self.last_attacker, self.last_defender, self.cards[:],self.board)

class RiskAction():
    """Stores the information about an action in a risk game"""
    
    def __init__(self, type, to_territory, from_territory, troops):
        """Initializes a RiskAction"""
        
        # What kind of action this is
        # types = (PreAssign, PrePlace, Place, TurnInCards, Attack
        # Occupy, Fortify)
        self.type = type
        
        # This stores the territory id of the place the action is going
        # For Each type it contains:
        #       PreAssign: The territory id being chosen by player
        #       PrePlace:  The territory id of the territory where troop is being placed
        #       Place: The territory id of the territory where troop is being placed
        #       TurnInCards: The card id of first of the cards being turned in, or None, if there are no cards to turn in
        #       Attack: The territory id of the territory being attacked
        #       Occupy: The territory id of the territory into which troops are moving
        #       Fortify: The territory id of the territory into which troops are moving
        self.to_territory = to_territory
        
        # This stores the territory id of the place the action is coming from
        # For Each type it contains:
        #       PreAssign: None
        #       PrePlace:  None
        #       Place: None
        #       TurnInCards: The card id of second of the cards being turned in, or None, if there are no cards to turn in
        #       Attack: The territory id of the territory doing the attacking
        #       Occupy: The territory id of the territory from which troops are moving
        #       Fortify: The territory id of the territory from which troops are moving
        self.from_territory = from_territory
        
        # This stores the number of troops involved in the action
        # For Each type it contains:
        #       PreAssign: None
        #       PrePlace:  None
        #       Place: None
        #       TurnInCards: The card id of third of the cards being turned in, or None, if there are no cards to turn in
        #       Attack: None
        #       Occupy: Number of troops moving into conquered territory
        #       Fortify: Number of troops moving to other territory
        self.troops = troops
        
    def print_action(self):
        """Displays information about this action to the output"""
        print self.description()
        
    def description(self, newline=False):
        d = ""
        d = d + str(self.type) 
        if newline:
            d = d + "\n"
        d = d + ' FROM: ' + str(self.from_territory) 
        if newline:
            d = d + "\n"
        d = d + ' TO: ' + str(self.to_territory) 
        if newline:
            d = d + "\n"
        d = d + ' NUM: ' + str(self.troops)
        return d
        
    def to_string(self):
        """Saves this action to a string"""
        s = 'RISKACTION|' + json.dumps(self.type) + '|' + json.dumps(self.from_territory) + '|' + json.dumps(self.to_territory) + '|' + json.dumps(self.troops)
        return s
        
    def from_string(self, s):
        """Loads this action from a string"""
        ss = s.split('|')
        if ss[0] != 'RISKACTION':
            print 'THIS IS NOT A RISK ACTION STRING!'
        self.type = json.loads(ss[1])
        self.from_territory = json.loads(ss[2])
        self.to_territory = json.loads(ss[3])
        self.troops = json.loads(ss[4])
        
def translateAction(state, action):
    """
    Takes a RiskAction and converts it into what needs to be returned by the AI to compete in the interactive risk game.
    Don't modify
    """
    
    if action.type == 'PreAssign' or action.type == 'PrePlace' or action.type == 'Place':
        return filter(lambda x:x.name == action.to_territory, riskengine.territories.values())[0]
    elif action.type == 'TurnInCards':
        if action.to_territory is None:
            return None,None,None
        else:
            return filter(lambda x:x.territory == state.board.territories[state.board.cards[action.to_territory].territory].name, riskengine.currentplayer.cards)[0],filter(lambda x:x.territory == state.board.territories[state.board.cards[action.from_territory].territory].name, riskengine.currentplayer.cards)[0],filter(lambda x:x.territory == state.board.territories[state.board.cards[action.troops].territory].name, riskengine.currentplayer.cards)[0]
    elif action.type == 'Attack':
        if action.to_territory is None:
            return None,None
        return filter(lambda x:x.name == action.from_territory, riskengine.territories.values())[0], filter(lambda x:x.name == action.to_territory, riskengine.territories.values())[0]
    elif action.type == 'Occupy':
        return action.troops
    elif action.type == 'Fortify':
        if action.to_territory is None:
            return None,None,0
        return filter(lambda x:x.name == action.from_territory, riskengine.territories.values())[0], filter(lambda x:x.name == action.to_territory, riskengine.territories.values())[0], action.troops
    else:
        print 'ILLEGAL ACTION TYPE!' 
        
def simulateAction(input_state, action):
    """
    Returns a list of all possible future states that this action could lead to, along with the probability of each.  For all but attack actions, there is only a single possibility.  
    This function makes a copy of the input_state, so it is not modified
    Returns: [state0, state1, ....], [probability0, probability1]
    """
    
    advance_player = False
    #Handle attacks differently, because there are multiple possible outcomes
    rstates = []
    rsprobs = []
    if action.type == 'Attack':
        rstates,rsprobs = simulateAttack(input_state, action)
    else:
        s = input_state.copy_state()
    
        if action.type == 'PreAssign':
            simulatePreAssignAction(s, action)
            advance_player = True
        elif action.type == 'PrePlace':
            simulatePrePlaceAction(s, action)
            advance_player = True
        elif action.type == 'TurnInCards':
            simulateTurnInCardsAction(s, action)
        elif action.type == 'Place':
            simulatePlaceAction(s, action)
        elif action.type == 'Occupy':
            simulateOccupyAction(s, action)
        elif action.type == 'Fortify':
            simulateFortifyAction(s, action)
            advance_player = True
        else:
            print 'ILLEGAL ACTION TYPE!' 
        
        rstates = [s]
        rsprobs = [1]
    
    for state in rstates:
        nextType(state, action)
        if advance_player:
            nextPlayer(state)
    
        #If it is the beginning of the turn, do the beginning of the turn stuff for the next player
        if advance_player and (state.turn_type == 'Place' or state.turn_type == 'TurnInCards'):
            beginTurn(state)    
        
    return rstates, rsprobs
        
        
def getReinforcementNum(state, player_id):
    #Count territories owned by the current player
    territory_num = state.owners.count(player_id)
    #Get that divided by three (with a min of three)
    territory_troops = int(max(3, math.floor(territory_num / 3.0)))
    
    #See if they own all of any continents
    continent_troops = 0
    for c in state.board.continents.itervalues():
        owned = True
        for t in c.territories:
            if state.owners[t] != player_id:
                owned = False
                break
        if owned:
            continent_troops = continent_troops + c.reward
        
    return territory_troops + continent_troops
        
def beginTurn(state):
    """
    Takes care of beginning-of-turn stuff (cards handled separately)
    Calculates new free armies from territories and continents
    """
    #Update the player's free armies count
    state.players[state.current_player].free_armies = getReinforcementNum(state, state.current_player)
    
def nextType(state, action):
    """Sets a state's turn type after an action is performed"""
    
    if action.type == 'PreAssign':
        #Move to PrePlace if all countries are owned
        if not None in state.owners:
            state.turn_type = 'PrePlace'
    elif action.type == 'PrePlace':
        #Move to Place if no one has any free armies left
        done = True
        for p in state.players:
            if p.free_armies > 0:
                done = False
        if done: 
            state.turn_type = 'Place'
    elif action.type == 'Place':
        if state.players[state.current_player].free_armies == 0:
            state.turn_type = 'Attack'
    elif action.type == 'TurnInCards':
        if len(state.players[state.current_player].cards) <= 3 or action.to_territory is None:
            state.turn_type = 'Place'
        if state.players[state.current_player].conquered_territory and len(state.players[state.current_player].cards) < 5:
            state.turn_type = 'Place'
    elif action.type == 'Attack':
        #If attack is over, change to Fortify
        if action.to_territory is None:
            state.turn_type = 'Fortify'
        elif state.armies[state.board.territory_to_id[action.to_territory]] == 0:
            #The attack was successful
            state.turn_type = 'Occupy'
            state.players[state.current_player].conquered_territory = True
        if max(state.owners) == min(state.owners):
            #GAME OVER IN THIS STATE
            state.turn_type = 'GameOver'

    elif action.type == 'Occupy':
        #Moved troops in, still attacking
        state.turn_type = 'Attack'
        if len(state.players[state.current_player].cards) > 5:
            #If this player has too many cards from defeating someone, must turn them in now (THIS Needs to happen after occupy)
            state.turn_type = 'TurnInCards'
        
    elif action.type == 'Fortify':
        #Done with turn, now next players turn
        state.turn_type = 'TurnInCards'
    else:
        print 'ILLEGAL ACTION TYPE!'
        
def getAllowedActions(state):
    """
    Returns a list of allowed actions in this current state.  
    An AI Agent simply has to select one of these
    """
      
    if state.turn_type == 'PreAssign':
        return getPreAssignActions(state)
    elif state.turn_type == 'PrePlace':
        return getPrePlaceActions(state)
    elif state.turn_type == 'Place':
        return getPlaceActions(state)
    elif state.turn_type == 'TurnInCards':
        return getTurnInCardsActions(state)
    elif state.turn_type == 'Attack':
        return getAttackActions(state)
    elif state.turn_type == 'Occupy':
        return getOccupyActions(state)
    elif state.turn_type == 'Fortify':
        return getFortifyActions(state)
    else:
        print 'THE STATE\'S TURN PHASE OF > ', state.turn_type, '< IS NOT VALID'

def getPreAssignActions(state):
    """Returns a list of all the PreAssign actions possible in this state"""
    
    #An Action is to select an unoccupied territory
    actions = []
    
    for i in range(len(state.owners)):
        if state.owners[i] is None:
            to_territory = state.board.territories[i].name
            a = RiskAction('PreAssign', to_territory, None, None)
            actions.append(a)
            
    return actions

def simulatePreAssignAction(state, action):
    """Execute the given action in the given state.  This will modify the state to 
    reflect the outcome of the state."""

    idx = state.board.territory_to_id[action.to_territory]
    
    if state.owners[idx] != None or state.armies[idx] != 0 or state.players[state.current_player].free_armies < 1:
        print 'INVALID PREASSIGN ACTION!'
        
    state.owners[idx] = state.current_player
    state.armies[idx] = 1
    state.players[state.current_player].free_armies -= 1
    
def getPrePlaceActions(state):
    """Returns a list of all the PrePlace actions possible in this state"""
    
    #An action is to place a troop in a territory occupied by the current player
    actions = []
    
    for i in range(len(state.owners)):
        if state.owners[i] == state.current_player:
            to_territory = state.board.territories[i].name
            a = RiskAction('PrePlace', to_territory, None, None)
            actions.append(a)
            
    return actions

def simulatePrePlaceAction(state, action):
    """Execute the given action in the given state.  This will modify the state to 
    reflect the outcome of the state."""
    
    idx = state.board.territory_to_id[action.to_territory]
    if state.owners[idx] == state.current_player and state.players[state.current_player].free_armies > 0:
        state.armies[idx] = state.armies[idx] + 1
        state.players[state.current_player].free_armies -= 1
    else:
        print 'INVALID PREPLACE ACTION:'
        print 'NO PREPLACE ACTION WILL OCCUR'
    
def getTurnInCardsActions(state):
    """Returns a list of all the TurnInCards actions possible in this state"""
    actions = []

    if len(state.players[state.current_player].cards) >= 3:
        for i1 in range(len(state.players[state.current_player].cards)-2):
            c1 = state.players[state.current_player].cards[i1]
            for i2 in range(i1+1, len(state.players[state.current_player].cards)-1):
                c2 = state.players[state.current_player].cards[i2]
                for i3 in range(i2+1, len(state.players[state.current_player].cards)):
                    c3 = state.players[state.current_player].cards[i3]
                    if isCardSet(state, c1, c2, c3):
                        a = RiskAction('TurnInCards', c1, c2, c3)
                        actions.append(a)
    
    if len(state.players[state.current_player].cards) < 5:
        #Don't have to turn in yet, so make a Non-Action
        a = RiskAction('TurnInCards', None, None, None)
        actions.append(a)
    
    return actions

def isCardSet(state, c1, c2, c3):
    """See if this trio of cards can be turned in (is it a set)"""
    
    #Get the pictures on the cards
    p1 = state.board.cards[c1].picture
    p2 = state.board.cards[c2].picture
    p3 = state.board.cards[c3].picture
    
    #If there is one wildcard in the set then it must be a set
    if 'Wildcard' in [p1,p2,p3]:
        return True
    #No wildcards, so are they all the same kind?
    if p1 == p2 and p2 == p3:
        return True
    else:
        #Not all the same, so they have to all be different
        #i.e. if any are the same, then they aren't a set
        if p1==p2 or p1==p3 or p2==p3:
            return False
    #The only case that gets here is when they are all different, so a set
    return True

def pause():
    """Utility if you ever want to pause to see output at some point."""
    i = raw_input('Paused. Press a key to continue . . . ')
    
def getTurnInValue(state):
    """See what the current turn-in-value is"""
    
    value = 0
    if state.turn_in_number >= len(state.board.turn_in_values):
        #Calculate turn in, more than scripted values
        value = state.board.turn_in_values[-1] + state.board.increment_value * (state.turn_in_number - len(state.board.turn_in_values) + 1)
    else:
        #Just grab scripted value
        value = state.board.turn_in_values[state.turn_in_number]
        
    state.turn_in_number = state.turn_in_number + 1
    return value
    
def simulateTurnInCardsAction(state, action):
    """
    Execute the given action in the given state.  This will modify the state to 
    reflect the outcome of the state.
    """
    #See if they want to turn in cards
    if action.to_territory is None:
        return
        
    if (not isCardSet(state, action.to_territory, action.from_territory, action.troops)) or action.to_territory not in state.players[state.current_player].cards or action.from_territory not in state.players[state.current_player].cards or action.troops not in state.players[state.current_player].cards:
        print 'INVALID TURN-IN-CARDS ACTION!'
        action.print_action()
        print 'NO TURN-IN-CARDS ACTION WILL BE TAKEN'
        
    #Modify cards appropriately (cards indices are stored in to_territory, from_territory, and troops
    #Add turn in value to players free_armies
    turn_in_troops = getTurnInValue(state)
    state.players[state.current_player].free_armies  += turn_in_troops
    
    #Add two troops to any territory that appears on one of the cards owned by this player
    for i in [action.from_territory, action.to_territory, action.troops]:
        t = state.board.cards[i].territory
        if state.owners[t] == state.current_player:
            state.armies[t] = state.armies[t] + 2
        #Remove these cards from the player's hand
        state.players[state.current_player].cards.remove(i)
    
def getPlaceActions(state):
    """Returns a list of all the Place actions possible in this state"""
    #An action is to place a troop in a territory occupied by the current player
    actions = []
    
    for i in range(len(state.owners)):
        if state.owners[i] == state.current_player:
            to_territory = state.board.territories[i].name
            a = RiskAction('Place', to_territory, None, None)
            actions.append(a)
            
    return actions

def simulatePlaceAction(state, action):
    """
    Execute the given action in the given state.  This will modify the state to 
    reflect the outcome of the state.
    """
    idx = state.board.territory_to_id[action.to_territory]
    if state.owners[idx] == state.current_player and state.players[state.current_player].free_armies >= 1:
        state.armies[idx] = state.armies[idx] + 1
        state.players[state.current_player].free_armies -= 1
    else:
        print 'INVALID PLACE ACTION: '
        action.print_action()
        print 'NO PLACE ACTION WILL OCCUR'
    
def getAttackActions(state):
    """Returns a list of all the Attack actions possible in this state"""
    
    #An action is to attack another territory from a territory owned by the current_player where 2 or more troops are
    actions = []
    
    for i in range(len(state.owners)):
        if state.owners[i] == state.current_player and state.armies[i] >= 2:
            from_territory = state.board.territories[i].name
            for n in state.board.territories[i].neighbors:
                if state.owners[n] != state.current_player:
                    to_territory = state.board.territories[n].name
                    a = RiskAction('Attack', to_territory, from_territory, None)
                    actions.append(a)
    
    no_action = RiskAction('Attack', None, None, None)
    actions.append(no_action)
    
    return actions

def getNumAttackSuccessors(state, action):
    """
    Determines how many possible states could result from this attack action
    This will determine how many successor states we create for the attack action
    """
    
    #Get indices of involved territories
    a_idx = state.board.territory_to_id[action.from_territory]
    d_idx = state.board.territory_to_id[action.to_territory]
  
    #Get number of dice that will be involved (This assumes attacker always attacks with all dice)
    a_num_dice = min(3, state.armies[a_idx]-1)
    d_num_dice = min(2, state.armies[d_idx])
    
    #The number of possible future states will be the minimum of the dice amounts + 1
    return min(a_num_dice, d_num_dice) + 1
    
    
def getAttackOutcome(a_num_dice, d_num_dice, outcome_index):
    """
    This will compute the probability of the outcome_index'th possible 
    result of a battle between the given number of dice.
    It will return the attacker_loss, defender_loss, outcome_probability
    """
    
    #Index by attacker dice, defender dice, outcome number
    outcome_probabilities = [[[0.4167, 0.5833], [0.2546, 0.7454]],[[0.5787, 0.4213],[0.2276, 0.3241, 0.4483]],[[0.6597, 0.3404],[0.3717, 0.3358, 0.2926]]]
    
    #print 'Getting attack outcome for : ', a_num_dice, ' : ', d_num_dice, ' : ', outcome_index
    
    attacker_loss = 0
    defender_loss = 0
    outcome_probability = outcome_probabilities[a_num_dice-1][d_num_dice-1][outcome_index]
    total_loss = min(a_num_dice, d_num_dice)
    
    if total_loss == 1:
        if outcome_index == 0:
            defender_loss = 1
        elif outcome_index == 1:
            attacker_loss = 1
        else:
            print 'Attack Outcome Index invalid'
        
    elif total_loss == 2:
        if outcome_index == 0:
            defender_loss = 2
        elif outcome_index == 1:
            defender_loss = 1
            attacker_loss = 1
        elif outcome_index == 2:
            attacker_loss = 2
        else:
            print 'Attack Outcome index invalid'
    else:
        print 'Total Loss is invalid.  It is: ', total_loss, ' A Num Dice: ', a_num_dice, 'D Num Dice: ', d_num_dice, ' Outcome Index: ', outcome_index
   
    return attacker_loss, defender_loss, outcome_probability
   
def simulateAttack(input_state, action):
    """
    Simulates attack action.  Returns a list of possible successor states and a 
    list of their probabilities.  This copies the input_state, so it is not modified.
    """
    
    if action.from_territory is None:
        #This is the end of attack action.  Give the player a card if they earned it
        cur_state = input_state.copy_state()
        
        if cur_state.players[cur_state.current_player].conquered_territory:
            not_duplicate = False
            card = random.choice(cur_state.cards)
            while not_duplicate:
                #Randomly choose a card and give it to this player
                card = random.choice(cur_state.cards)
                if card not in cur_state.players[cur_state.current_player].cards:
                    not_duplicate = True
            cur_state.players[cur_state.current_player].cards.append(card)
            #Reset the players conquered_territory flag
            cur_state.players[cur_state.current_player].conquered_territory = False
            
        return [cur_state], [1]
    
    #How many possible attack outcomes are there
    num_successors = getNumAttackSuccessors(input_state, action)
    
    successor_states = []
    successor_probs = []
    
    for i in range(num_successors):
        cur_state = input_state.copy_state()
        cur_prob = 0
        if action.type == 'Attack':
            cur_prob = simulateAttackAction(cur_state, action, i)
        else:
            print 'ILLEGAL ACTION TYPE'
        
        nextType(cur_state, action)
        successor_states.append(cur_state)
        successor_probs.append(cur_prob)
        
    return successor_states, successor_probs
   
def simulateAttackAction(state, action, outcome_index):
    """
    Execute the given action in the given state, assuming that the outcome of the battle is given by outcome_index.  This will modify the state to 
    reflect the outcome of the state.
    """            
    #a is attacker and d is defender
    
    #Get indices of involved territories
    a_idx = state.board.territory_to_id[action.from_territory]
    d_idx = state.board.territory_to_id[action.to_territory]
  
    #MAKE SURE THIS IS VALID
    if state.owners[a_idx] != state.current_player or state.owners[d_idx] == state.current_player or state.armies[a_idx] <= 1: 
        print 'INVALID ATTACK ACTION: '
        action.print_action()
        print 'NO ATTACK ACTION WILL BE TAKEN'
        return 
  
    #Set last attacker and defender variables in the state
    state.last_attacker = a_idx
    state.last_defender = d_idx
  
    #Player id of defender
    defender = state.owners[d_idx]
  
    #Get number of dice that will be involved (This assumes attacker always attacks with all dice)
    a_num_dice = min(3, state.armies[a_idx]-1)
    d_num_dice = min(2, state.armies[d_idx])

    if state.armies[d_idx] == 0:
        print 'THERE ARE NO ARMIES IN TERRITORY: ', state.board.territories[d_idx].name
        print 'ACTION: ', action.print_action()
        print 'State: ', state.print_state()
    
    #print 'Number of attacker armies : ', state.armies[a_idx]
    #print 'Number of defender armies : ', state.armies[d_idx]
    #print 'Attack with : ', a_num_dice, 'attacker dice, and ', d_num_dice, 'defender dice'
    
    #Get the outcome and probability for the input outcome index
    a_loss, d_loss, outcome_probability = getAttackOutcome(a_num_dice, d_num_dice, outcome_index)
    
    state.armies[d_idx] = max(state.armies[d_idx] - d_loss, 0)
    state.armies[a_idx] = state.armies[a_idx] - a_loss
    
    #Check if the defender is at zero, then change owner (armies will be moved in with the next action (Occupy)
    if state.armies[d_idx] == 0:
        state.owners[d_idx] = state.current_player
        
    #Check to see if the defender is now done completely, in which case we need to give her cards to the attacker.
    if defender not in state.owners:
        #The defender is done
        state.players[state.current_player].cards.extend(state.players[defender].cards)
        state.players[defender].cards = []
    
    return outcome_probability
    
def getOccupyActions(state):
    """Returns a list of all the Occupy actions possible in this state"""
    
    #An action is to move an amount of troops into the newly conquered country (must leave at least 1 behind, and must move at least min(3,number_there -1))
    actions = []
    
    if state.last_defender is None or state.last_attacker is None:
        return actions
    
    to_territory = state.board.territories[state.last_defender].name
    from_territory = state.board.territories[state.last_attacker].name
        
    for k in range(min(state.armies[state.last_attacker]-1,3), state.armies[state.last_attacker]):
        a = RiskAction('Occupy', to_territory, from_territory, k)
        actions.append(a)
        
    return actions
    
def simulateOccupyAction(state, action):    
    """
    Execute the given action in the given state.  This will modify the state to 
    reflect the outcome of the state.
    """
    to_idx = state.board.territory_to_id[action.to_territory]
    from_idx = state.board.territory_to_id[action.from_territory]
    #Make sure that the occupy action is correctly constructed
    if to_idx != state.last_defender or from_idx != state.last_attacker or state.armies[from_idx] - action.troops < 1 or state.owners[from_idx] != state.current_player or state.owners[to_idx] != state.current_player:
        #This move is invalid
        print 'INVALID OCCUPY ACTION: '
        action.print_action()
        print 'To index = ', to_idx
        print 'Last defender = ', state.last_defender
        print 'From index = ', from_idx
        print 'Last attacker = ', state.last_attacker
        
        print 'NO OCCUPY ACTION WILL BE TAKEN'
        pause()
        return 

    state.armies[to_idx] = state.armies[to_idx] + action.troops
    state.armies[from_idx] = state.armies[from_idx] - action.troops
    
def getFortifyActions(state):
    """Returns a list of all the Fortify actions possible in this state"""
    
    #An action is to move troops from one territory to a neighboring territory (both owned by current_player), leaving at least 1 troop in the from_territory
    actions = []
    
    for i in range(len(state.owners)):
        if state.owners[i] == state.current_player and state.armies[i] >= 2:
            from_territory = state.board.territories[i].name
            for n in state.board.territories[i].neighbors:
                if state.owners[n] == state.current_player:
                    to_territory = state.board.territories[n].name
                    for k in range(1, state.armies[i]):
                        a = RiskAction('Fortify', to_territory, from_territory, k)
                        actions.append(a)
                        
    no_action = RiskAction('Fortify', None, None, 0)
    actions.append(no_action)
    
    return actions    
    
def simulateFortifyAction(state, action):
    """
    Execute the given action in the given state.  This will modify the state to 
    reflect the outcome of the state.
    """
    if action.to_territory is None:
        return
        
    to_idx = state.board.territory_to_id[action.to_territory]
    from_idx = state.board.territory_to_id[action.from_territory]
    
    #Make sure that the fortify action is correctly constructed
    if state.armies[from_idx] - action.troops < 1 or state.owners[from_idx] != state.current_player or state.owners[to_idx] != state.current_player or to_idx not in state.board.territories[from_idx].neighbors:
        #This move is invalid
        print 'INVALID FORTIFY ACTION: '
        action.print_action()
        print 'NO FORTIFY ACTION WILL BE TAKEN'
        return 
        
    state.armies[to_idx] = state.armies[to_idx] + action.troops
    state.armies[from_idx] = state.armies[from_idx] - action.troops
    
def createRiskBoard():
    """Creates a RiskBoard from the current riskengine state.  Used to interface with the GUI that allows humans to play the AIs"""
    
    board = RiskBoard()
    
    #Create Continents
    for c in riskengine.continents:
        rc = RiskContinent(c[0],c[1])
        board.add_continent(rc)
        
    #Create Territories
    id_counter = 0
    for t in riskengine.territories.values():
        rt = RiskTerritory(t.name, id_counter)    
        board.add_territory(rt)
        tc = board.continents[t.continent]
        tc.add_territory(rt.id)
        id_counter += 1
    
    #Add in neighbors of each territory
    for t in riskengine.territories.values():
        rt = board.territories[board.territory_to_id[t.name]]
        for n in t.neighbors:
            rt.add_neighbor(board.territory_to_id[n.name])
    
    #Create cards
    for c in riskengine.allcards:
        rc = RiskCard(board.territory_to_id[c.territory], c.picture, len(board.cards))
        board.add_card(rc)
        
    #Create and add players
    id_counter = 0
    for p in riskengine.playerorder:
        rp = RiskPlayer(p.name, id_counter, p.freeArmies, p.conqueredTerritory)
        id_counter += 1
        for c in p.cards:
            rc = RiskCard(board.territory_to_id[c.territory], c.picture, len(board.cards))
            board.add_card(rc)
            rp.add_card(board.card_to_id[board.territories[board.territory_to_id[c.territory]].name])
        board.add_player(rp)
        
    board.set_turn_in_values(riskengine.cardvals)
    board.set_increment_value(riskengine.incrementval)
        
    return board
    
def createRiskState(board, function_name, occupying=None):
    """Creates a RiskState from the current riskengine state.  Used to interface with the GUI that allows humans to play the AIs"""

    #players, armies, owners, current_player, turn_type
    #Create players
    players = []
    id_counter = 0
    for p in riskengine.playerorder:
        rp = RiskPlayer(p.name, id_counter, p.freeArmies, p.conqueredTerritory)
        for c in p.cards:
            rp.add_card(board.card_to_id[c.territory])
        players.append(rp)
        id_counter += 1
    
    #Create armies and owners
    armies = [0]*len(board.territories)
    owners = [None]*len(board.territories)
    for t in riskengine.territories.values():
        idx = board.territory_to_id[t.name]
        if t.player is not None:
            armies[idx] = t.armies
            owners[idx] = board.player_to_id[t.player.name]
    
    #Determine the current player
    current_player_obj = filter(lambda x:x.name == riskengine.currentplayer.name, players)[0]
    current_player = current_player_obj.id

    turn_type = None
    if riskengine.phase == 'Preposition' and function_name == 'Assignment':
        turn_type = 'PreAssign'
    elif riskengine.phase == 'Preposition' and function_name == 'Placement':
        turn_type = 'PrePlace'
    elif riskengine.phase == 'Place' and function_name == 'Placement':
        turn_type = 'Place'
    elif riskengine.phase == 'Place' and function_name == 'TurnInCards':
        turn_type = 'TurnInCards'
    elif riskengine.phase == 'Attack' and function_name == 'Attack':
        turn_type = 'Attack'
    elif riskengine.phase == 'Attack' and function_name == 'Occupation':
        turn_type = 'Occupy'
    elif riskengine.phase == 'Attack' and function_name == 'Fortification':
        turn_type = 'Fortify'
            
    #current card turn in index
    turn_in_number = riskengine.currentcard
            
    #Determine last attacker and defender
    last_attacker = None
    last_defender = None
    if occupying is not None:
        last_attacker = board.territory_to_id[occupying[0]]
        last_defender = board.territory_to_id[occupying[1]]
        
    #Create Cards
    cards = []
    for c in riskengine.allcards:
        cards.append(board.card_to_id[c.territory])
       
    state = RiskState(players,armies,owners,current_player,turn_type,turn_in_number, last_attacker, last_defender, cards, board)

    return state
    
    
def getInitialState(board):
    """Get the initial state for this board.  Shuffles the player order."""
    #Initialize the state with the information in the board

    free_armies = 45 - 5*(len(board.players)-1)
    

    state_players = []
    for p in board.players:
        new_player = p.copy_player()
        state_players.append(new_player)
        new_player.free_armies = free_armies
             
    #Initialize other state elements
    armies = [0]*len(board.territories)
    owners = [None]*len(board.territories)
    current_player = 0
    turn_type = 'PreAssign'
    turn_in_number = 0
    last_attacker = None
    last_defender = None
    
    #Cards
    cards = [0]*len(board.cards)
    for i in range(len(cards)):
        cards[i] = board.cards[i].id
    
    state = RiskState(state_players, armies, owners, current_player, turn_type, turn_in_number, last_attacker, last_defender, cards, board)
    return state
    
    
def loadBoard(filename):
    """Loads a RiskBoard from the given filename"""
    
    #Open the zip file to get map data
    zfile = zipfile.ZipFile(filename)
    board = RiskBoard()
    loadTerritories(zfile, board)
    
    #Close the zip file
    zfile.close()

    return board
    
def loadTerritories(zfile, board):
    """Load territory (and other) information from a file."""
   
    terr = xml.dom.minidom.parseString(zfile.read("territory.xml"))
    
    terr_structs = terr.getElementsByTagName("territory")
    
    #Create and add territories
    for t in terr_structs:
        name = t.getAttribute("name")
        nt = RiskTerritory(name, len(board.territories))
        board.add_territory(nt)
    
    #Create continents, add in neighbors
    for terrs in terr_structs:
        name = terrs.getAttribute("name")
        cname = terrs.getAttribute("continent")
        tidx = board.territory_to_id[name]
        ncon = RiskContinent(cname, 0)
        board.add_continent(ncon)
        continent = board.continents[cname]
        continent.add_territory(tidx)
        
        neighbors = terrs.getElementsByTagName("neighbor")
        for neigh in neighbors:
            nidx = board.territory_to_id[neigh.childNodes[0].data]
            board.territories[tidx].add_neighbor(nidx)
        
    cont_structs = terr.getElementsByTagName("continent")
    for con in cont_structs:
        continent = board.continents[con.getAttribute("name")] 
        continent.reward = int(con.getAttribute("value"))
        
    loadCards(terr, board)
    
def loadCards(xmlFile, board):
    """Load the data for the cards from the file."""

    cardvals = []
    card = xmlFile.getElementsByTagName("cards")[0]
    for pic in card.getElementsByTagName("picture"):
        board.pictures.append(pic.childNodes[0].data)
    for cvalue in card.getElementsByTagName("card"):
        cardvals.append(int(cvalue.childNodes[0].data))
        
    incremtag = card.getElementsByTagName("increase")[0]
    incrementval = int(incremtag.childNodes[0].data)
    
    board.set_turn_in_values(cardvals)
    board.set_increment_value(incrementval)
    
    createCards(board)
    
def createCards(board):
    """Create the set of cards."""
    
    wildcard = "Wildcard"
    for terr in range(2):
        car = RiskCard(terr, wildcard, terr)
        board.add_card(car)
    for terr in range(2, len(board.territories)):
        car = RiskCard(terr, random.choice(board.pictures), terr)
        board.add_card(car)
        
    board.shuffle_cards()
    