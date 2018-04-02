import random
import sys
from operator import attrgetter

# Import custom libraries
sys.path.append('pa2_support')
from aihelper import *
from turbohelper import *
from risktools import *
from pa2_learn_d_tree import *

# === attackAction() Constants ===
CONFIDENCE_RATIO = 0.65
SAFETY_RATIO = 0.6
TERRITORY_RATIO = 0.4
# ================================

# Decision Tree Container Cache
MY_DTREE_LOCATION = 'BigCheese.dtree'
#MY_DTREE_LOCATION = 'pa2_trees/pa2_treesataset_1000_cheese_ai_cheese_cheese_ai_cheese2_20141203-105649_7.dtree'
MY_DTREE_SAMPLE_SIZE = 100
myDTree = None
nodestolookat=[]

#=============================================================================================================
#=============================================== Action Functions ============================================
#=============================================================================================================
class SearchNode():
    def __init__(self,action,state,path,h): 
        self.action = action       
        self.state = state
        self.path = path
        self.h = h




def Recusive_Depth_Limited_DFS(Node,limit):
    if limit == 1:
        print '1'
        global nodestolookat
        nodestolookat.append(Node)    

    elif limit == 0:      
        return "cutoff"
    else:
        cutoff = False
        
        moves = getAllowedActions(Node.state)      

        for m in moves:
            successors, probabilities = simulateAction(Node.state, m)
            for succes in successors:
                new_state = SearchNode(m,succes, Node.path.append(Node),heuristic(succes,m))
                result = Recusive_Depth_Limited_DFS(new_state,limit-1)
                if result is "cutoff":
                    cutoff = True
                elif result is not "falure" :
                    return result 

    if cutoff == True:
        return "cutoff"
    else:
        return "falure"

def attacksearch(state):
    global nodestolookat
    nodestolookat=[]
    start=SearchNode(state,0,state,0)
    result=Recusive_Depth_Limited_DFS(start,3)
    if result:
        #TODO sort nodestolookat by heristic and choose path[0] of the highest node
        return nodestolookat[0].path[0]


#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""

    #Get the possible actions in this state
    actions = getAllowedActions(state)

    if state.turn_type == 'PreAssign':
        myaction = preAssignAction(state, actions)
        #myaction= random.choice(actions)

    elif state.turn_type == 'Place':
        myaction = placeAction(state, actions)

    elif state.turn_type == 'Attack': 
        #myaction = attackAction(state,  actions)
        myaction= Simulate(state, actions)
        #myaction = attacksearch(state)

    elif state.turn_type == 'Fortify':
        myaction = fortifyAction(state,  actions)

    elif state.turn_type == 'PrePlace':
        myaction = prePlaceAction(state,  actions)

    elif state.turn_type == 'Occupy':
        myaction = occupyAction(state,  actions)

    elif state.turn_type == 'TurnInCards':
        myaction = turnInCardsAction(state,  actions)

    else:
        print 'Error - Undefined Turn Type: ',  state.turn_type,  ', Taking random action.'
        return random.choice(actions)

    return myaction



def Simulate(state,  actions):
    #print 'Heuristic AI : Player', state.players[state.current_player].name, 'considering', len(actions), 'actions'
    
    #To keep track of the best action we find
    best_action = None
    best_action_value = None
    
    #Evaluate each action
    for a in actions:
               
        #Simulate the action, get all possible successors
        successors, probabilities = simulateAction(state, a)
              
        #Compute the expected heuristic value of the successors
        current_action_value = 0.0
        
        for i in range(len(successors)):
            #Each successor contributes its heuristic value * its probability to this action's value
            
            current_action_value += (heuristic(successors[i], a) * probabilities[i])
        
        #Store this as the best action if it is the first or better than what we have found
        if best_action_value is None or current_action_value > best_action_value:
            best_action = a
            best_action_value = current_action_value
        
    #Return the best action
    return best_action

def heuristic(state, action):    
    """Returns a number telling how good this state is"""
        # 2. Are we in it for the number of territories, or just staying alive (liberal or conservative play)
    if action.to_territory is None:
       return 0
    numOfTerritoriesOwned = state.owners.count(state.current_player)
    numOfTerritories = len(state.owners)
    numOfTerritoriesOwnedRatio = numOfTerritoriesOwned / numOfTerritories
    # Create enemy and friend territories from the input
    enemy = Territory(state,  state.board.territory_to_id[action.to_territory]) 
    friend = Territory(state,  state.board.territory_to_id[action.from_territory])

    # Get all the neighbors
    friendlyNeighbors = Neighbors(state,  friend.getIndex())
    enemyNeighbors = Neighbors(state,  enemy.getIndex())

    # Friendly neighbor statistics
    f_numOfNeighbors = float(len(friendlyNeighbors.getNeighbors()))
    f_numOfFriendlyNeighbors = float(len(friendlyNeighbors.getFriendlyNeighbors()))

    # Enemey neighbor statistics
    e_numOfNeighbors = float(len(enemyNeighbors.getNeighbors()))
    e_numOfFriendlyNeighbors = float(len(enemyNeighbors.getFriendlyNeighbors()))

    # Calculate the win probability
    winProbability = float(friend.getArmies()) / float(friend.getArmies() + enemy.getArmies())

    # Calculate the occupied ratios
    f_occupiedRatio = f_numOfFriendlyNeighbors / f_numOfNeighbors
    e_occupiedRatio = e_numOfFriendlyNeighbors / e_numOfNeighbors
    
    safetyRatio = f_occupiedRatio * e_occupiedRatio  
    return f_occupiedRatio+numOfTerritories


# Ryan Nazaretian's attack action picker
def attackAction(state,  actions):

    # 1. If there are no possible moves, yet we have a territory (which will probably get crushed in the next move), take the default action
    # If the action list has one element, then that means we only have one move available, which is to do nothing
    if(len(actions) == 1):
        return actions[0]

    # 2. Are we in it for the number of territories, or just staying alive (liberal or conservative play)
    numOfTerritoriesOwned = state.owners.count(state.current_player)
    numOfTerritories = len(state.owners)
    numOfTerritoriesOwnedRatio = numOfTerritoriesOwned / numOfTerritories

    # 3. Calculate the win probability and safety ratio of each action
    formattedActions = []
    for action in actions[:-1]:
        # Create enemy and friend territories from the input
        enemy = Territory(state,  state.board.territory_to_id[action.to_territory]) 
        friend = Territory(state,  state.board.territory_to_id[action.from_territory])

        # Get all the neighbors
        friendlyNeighbors = Neighbors(state,  friend.getIndex())
        enemyNeighbors = Neighbors(state,  enemy.getIndex())

        # Friendly neighbor statistics
        f_numOfNeighbors = float(len(friendlyNeighbors.getNeighbors()))
        f_numOfFriendlyNeighbors = float(len(friendlyNeighbors.getFriendlyNeighbors()))

        # Enemey neighbor statistics
        e_numOfNeighbors = float(len(enemyNeighbors.getNeighbors()))
        e_numOfFriendlyNeighbors = float(len(enemyNeighbors.getFriendlyNeighbors()))

        # Calculate the win probability
        winProbability = float(friend.getArmies()) / float(friend.getArmies() + enemy.getArmies())

        # Calculate the occupied ratios
        f_occupiedRatio = f_numOfFriendlyNeighbors / f_numOfNeighbors
        e_occupiedRatio = e_numOfFriendlyNeighbors / e_numOfNeighbors

        # Safety ratio is the percentage of neighbors of our 'friend' that are friends, times the percentange of neighbors of our 'enemy' that are friends (1-prob of enemy)
        safetyRatio = f_occupiedRatio * e_occupiedRatio

        # If we don't have many terirtories (% owned < TERRITORY RATIO), then only take probable win risks
        # I'm not sure if this decision helps our chances of winning or not
        if(numOfTerritoriesOwnedRatio < TERRITORY_RATIO or safetyRatio < winProbability):
            formattedActions.append({'WinProbability': winProbability, 'safetyRatio':  safetyRatio, 'Action': action})
        else:        
            formattedActions.append({'safetyRatio':  safetyRatio, 'WinProbability': winProbability, 'Action': action})

    # 4. Sort the actions by the best chances of winning (greatest to least)
    formattedActions.sort(reverse = True)

    # 5. Select the action (the one with the highest probability of winning, which is the last element)
    for action in formattedActions:
        if(action['WinProbability'] >= CONFIDENCE_RATIO or (action['safetyRatio'] >= SAFETY_RATIO and numOfTerritoriesOwnedRatio >= TERRITORY_RATIO)): # Ratio Test
            return action['Action']

    # 6. Return the default case - this happens if there are no actions that meet our conditions in 5
    return actions[-1]

# TODO this is what Dr. Archibald's code did 
def preAssignAction(state, actions):

    #Set up the data instance to pass into the decision tree
    global myDTree
    if myDTree is None:
        print 'Loading DTree'
        myDTree = loadDTree(MY_DTREE_LOCATION)
        print 'Done.'

    #Are we the first player?
    first_player = 0
    if state.current_player == 0:
        first_player = 1

    owners = state.owners[:]
    for t in range(len(owners)):
        if owners[t] == state.current_player:
            owners[t] = 1
        elif owners[t] is not None:
            owners[t] = 0

    owners.insert(0,first_player)

    best_v = -1
    best_a = None

    for a in actions:
        instance = owners[:]
        instance[state.board.territory_to_id[a.to_territory]+1] = 1
        # av = evaluateAssignAction(instance, a) - Implemented below

        #======================================================================
        # evaluateAssignAction(instance, action) - Note that 'action' (a) was never used in this function, but it was passed in! Weird!
        snones = []
        #minor change to his code i think this is what he was really going for
        for t in range(len(instance)):
           if instance[t] is None:
                snones.append(t)
        #for t in range(len(instance)):
        #   if t is None:
        #        snones.append(t)
    

        action_value = 0

        for s in range(MY_DTREE_SAMPLE_SIZE):
            new_owner = False
            nones = snones[:]

            while len(nones) > 0:
                nt = random.choice(nones)
                nones.remove(nt)
                instance[nt] = int(new_owner)
                new_owner = not new_owner

            action_value  += myDTree.get_prob_of_win(instance)

        # return float(action_value) / float(MY_DTREE_SAMPLE_SIZE)
        av = float(action_value) / float(MY_DTREE_SAMPLE_SIZE)
        #======================================================================

        if av > best_v:
            best_v = av
            best_a = a

    return best_a

# Ryan Smith's defensive place action code
def placeAction(state, actions):
##    priorityactions=[]
##    for a in actions:
##        if a.to_territory is not None:
##            d=0
##            for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors[:]:
##                if state.owners[n] != state.current_player:
##                    d+=state.armies[n]
##            if(d > 0):
##                priorityactions.append(dangerData(a, float(d)/float(state.armies[state.board.territory_to_id[a.to_territory]])))
##    priorityactions=sorted(priorityactions, key=attrgetter('danger'))
##    if len(priorityactions) > 3:
##        return random.choice(priorityactions[len(priorityactions)/2:-1]).territory_id
##    elif len(priorityactions) > 0:
##        return random.choice(priorityactions).territory_id
##    else:
##        return actions[-1]
    action_prob=dict()
    territory_value=dict()
    action_value=dict()
    myaction=actions[0]
    for a in actions:
        if a.to_territory is not None:
            temp=0
            count=1
            m2=state.board.territory_to_id[a.to_territory]
            for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                if state.owners[n] != state.current_player:
                    temp+=(state.armies[n])
            territory_value[m2]=temp #state, value mapping
            action_value[a]=m2 #action , state mapping
                   
    max_value =float("-inf")
    for a in actions:
        if a.to_territory is not None:
            if action_value[a] in territory_value:
                if territory_value[action_value[a]]>max_value:
                    max_value=territory_value[action_value[a]]
                    myaction=a
        
    return myaction

# TODO  - Implement a better place action, this is what Dr. Archibald's code did  
def fortifyAction(state,  actions):

    action_prob=dict()
    territory_value=dict()
    action_value=dict()
    myaction=actions[0]
    for a in actions:
        if a.to_territory is not None:
            temp=0
            count=1
            m2=state.board.territory_to_id[a.to_territory]
            self_army=state.armies[m2]
            for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                if state.owners[n] != state.current_player:
                    temp+=(state.armies[n])
                    count=count+1
            temp=temp-self_army
            action_prob[a]=1.0/float(count)
            territory_value[m2]=temp #state, value mapping
            action_value[a]=m2 #action , state mapping

    for a in actions:
        if a.to_territory is not None:
            temp=0
            m2=state.board.territory_to_id[a.to_territory]
            for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                if n in territory_value:
                    temp=temp+action_prob[a]*territory_value[n]
            territory_value[m2]=temp

    for a in actions:
        if a.to_territory is not None:
            temp=0
            m2=state.board.territory_to_id[a.to_territory]
            for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                if n in territory_value:
                    temp=temp+action_prob[a]*territory_value[n]
            territory_value[m2]=temp
                   
    max_value =float("-inf")
    for a in actions:
        if a.to_territory is not None:
            if action_value[a] in territory_value:
                if territory_value[action_value[a]]>max_value:
                    max_value=territory_value[action_value[a]]
                    myaction=a
        
    return myaction

# TODO  - Implement a better place action, this is what Dr. Archibald's code did 
def prePlaceAction(state,  actions):
    action_prob=dict()
    territory_value=dict()
    action_value=dict()
    myaction=actions[0]
    for a in actions:
        if a.to_territory is not None:
            temp=0
            count=1
            m2=state.board.territory_to_id[a.to_territory]
            for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                if state.owners[n] != state.current_player:
                    temp+=(state.armies[n])
            territory_value[m2]=temp #state, value mapping
            action_value[a]=m2 #action , state mapping
                   
    max_value =float("-inf")
    for a in actions:
        if a.to_territory is not None:
            if action_value[a] in territory_value:
                if territory_value[action_value[a]]>max_value:
                    max_value=territory_value[action_value[a]]
                    myaction=a
        
    return myaction

# TODO  - Implement
def occupyAction(state,  actions):
    return random.choice(actions)

# TODO  - Implement
def turnInCardsAction(state,  actions):
    return random.choice(actions)

#=============================================================================================================
#=============================================== Custom Classes ==============================================
#=============================================================================================================

# Ryan Nazaretian's Neighbor Container Class
class Neighbors():
    def __init__(self,  state,  territoryIndex):
        # Get information about myself
        self.territory = Territory(state,  territoryIndex)

        # Create a list of all neighbors
        self.neighbors = []
        for neighbor in  state.board.territories[self.territory.getIndex()].neighbors:
            self.neighbors.append(Territory(state,  neighbor))

    # Returns a list of Territories that are neighbors
    def getNeighbors(self):
        return self.neighbors

    # Returns what Territory this neighborhood calculation was solved for
    def getTerritory(self):
        return self.territory

    # Returns a list of Enemy Territories that are neighbors
    def getEnemyNeighbors(self):
        enemyNeighbors = []
        for enemyN in self.neighbors:
            # Only get enemies (other player territories)
            if enemyN.isEnemy():
                enemyNeighbors.append(enemyN)
        return enemyNeighbors 

    # Returns a list of Friendly Territories that are neighbors
    def getFriendlyNeighbors(self):
        friendlyNeighbors = []
        # Only get friends (owner territories)
        for friendlyN in self.neighbors:
            if friendlyN.isFriendly():
                friendlyNeighbors.append(friendlyN)
        return friendlyNeighbors 

    # Prints the Territory with information about myself
    def printTerritory(self):
        self.territory.printTerritory()

    # Prints the list of all neighbors
    def printNeighbors(self):
        print '---My Territory: ',  self.territory.printTerritory()
        for neighbor in self.neighbors:
            neighbor.printTerritory()

    # Prints the list of enemy neighbors
    def printEnemyNeighbors(self):
        for enemyN in self.getEnemyNeighbors():
            enemyN.printTerritory()

    # Prints the list of friendly neighbors
    def printFriendlyNeighbors(self):
        for friendlyN in self.getFriendlyNeighbors():
            friendlyN.printTerritory()

# Ryan Nazaretian's Territory Data Container 
class Territory():
    def __init__(self,  state,  territory):
        # Index location in all the state arrays
        self.index = territory

        # Is owned by the current player (me)?
        self.friendly = (state.owners[territory] == state.current_player)

        # The string that represents the name of the territory
        self.name = state.board.territories[territory].name

        # The number of armies in this territory
        self.armies = state.armies[territory]

    # Returns True if the territory is owned by the current player
    def isFriendly(self):
        return self.friendly

    # Returns True if the territory is not owned by the current player
    def isEnemy(self):
        return not self.friendly

    # Returns the array index of the territory
    def getIndex(self):
        return self.index

    # Returns a string with the name of the territory
    def getName(self):
        return self.name

    # Returns the number of armies in the territory
    def getArmies(self):
        return self.armies

    # Prints the information for the territory
    def printTerritory(self):
        print 'Index: ', self.index, ', Name: ', self.getName(), ', Status: ',
        if(self.isFriendly()):
            print 'Friendly',
        if(self.isEnemy()):
            print 'Enemy',
        print ', Armies: ', self.getArmies()

# Ryan Smith's Danger Data class 
class dangerData():
    """The data structure used to store the data for learning the decision tree"""
    def __init__(self, territory_id,danger):
        self.territory_id=territory_id
        self.danger=danger


#=============================================================================================================
#=============================================== GUI Interfaces ==============================================
#=============================================================================================================

#Stuff below this is just to interface with Risk.pyw GUI version
#DO NOT MODIFY

class data():
    """The data structure used to store the data for learning the decision tree"""
    def __init__(self, territory_id,territoryarmies,   armiesnext):
        self.territory_id=territory_id
        self.territoryarmies=territoryarmies
        self.armiesnext=armiesnext    

def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    action = getAction(game_state)
    return translateAction(game_state, action)

def Assignment(player):
#Need to Return the name of the chosen territory
    return aiWrapper('Assignment')

def Placement(player):
#Need to return the name of the chosen territory
     return aiWrapper('Placement')

def Attack(player):
 #Need to return the name of the attacking territory, then the name of the defender territory    
    return aiWrapper('Attack')

def Occupation(player,t1,t2):
 #Need to return the number of armies moving into new territory      
    occupying = [t1.name,t2.name]
    aiWrapper('Occupation',occupying)

def Fortification(player):
    return aiWrapper('Fortification')
