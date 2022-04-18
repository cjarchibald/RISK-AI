import sys
import risktools
from queue import PriorityQueue

###### risk_search.py
#      This script will use Uniform Cost Search to determine if an attacking path exists in 
#      the game of RISK from a source territory (owned by the acting player)
#      to a destination territory (owned by an opposing player)
#      through territories owned by opposing players.  
#      A sequence of successful attacks could follow this path and occupy the destination territory
#      The students can explore different cost functions for the paths
#      It will do this for a given state from a logfile.
#      You can get the state number from the risk_game_viewer 
######

class SearchNode():
    """
    A data structure to store the nodes in our search tree
    """
    def __init__(self, territory_id, parent, step_cost):
        self.id = territory_id
        self.parent = parent
        self.cost = 0
        if parent:
            self.cost = parent.cost + step_cost

    def __eq__(self, other):
        return (self.cost == other.cost)

    def __ne__(self, other):
        return (self.cost != other.cost)

    def __lt__(self, other):
        return (self.cost < other.cost)

    def __le__(self, other):
        return (self.cost <= other.cost)

    def __gt__(self, other):
        return (self.cost > other.cost)

    def __ge__(self, other):
        return (self.cost >= other.cost)

#The actual search function
def search(fringe, goal, state):
    #List to store the expanded states on this search
    expanded = []

    #Continue until the fringe is empty
    while not fringe.empty():
       
       #
       #INSERT TASK 1.2 CODE HERE
       #
       break
       
    #If no path found, return none
    return None

#Set up and run a search from src territory to dst territory in state 
def run_search(src, dst, state):
    root = SearchNode(src,None,0.0)
    fringe = PriorityQueue()
    fringe.put(root)
    goal = search(fringe,dst,state)
    if goal:
        cur = goal
        path = []
        # Extract the path and print it out 
        while cur is not None:
            path.append(cur.id)
            cur = cur.parent

        #Reverse the path
        path.reverse()

        print('PATH FOUND! Cost = ', goal.cost)
        for p in path:
            print(' [', p, ']', state.board.territories[p].name)
    else:
        print('NO PATH FOUND!')

def get_successors(territory_id, state):
    """Return all of the neighbor territories of territory_id that aren't owned by the 
       current player in the given state"""
    successors = []

    #
    #INSERT TASK 1.1 CODE HERE
    #

    return successors

def print_usage():
    print('USAGE: python risk_search.py log_filename state_num source_territory destination_territory')

if __name__ == "__main__":
    #Get ais from command line arguments
    if len(sys.argv) != 5:
        print_usage()
        sys.exit()
    
    #get log file name
    logfilename = sys.argv[1]
    
    #Open the logfile
    logfile = open(logfilename, 'r')    
    
    #Get the state number
    state_number = int(sys.argv[2])

    #Get a state that we can use
    riskboard = risktools.loadBoard('world.zip')
    search_state = risktools.getInitialState(riskboard)

    #Get the source territory
    try:
        source_territory = riskboard.territory_to_id[sys.argv[3]]
    except:
        print(sys.argv[3], "not recognized as a valid territory! Exiting.")
        sys.exit()

    #Get the destination territory
    try:
        destination_territory = riskboard.territory_to_id[sys.argv[4]]
    except:
        print(sys.argv[4], "not recognized as a valid territory! Exiting.")
        sys.exit()

    print('Risk_search is searching from ', riskboard.territories[source_territory].name, 'to', riskboard.territories[destination_territory].name, 'in logfile', logfilename, 'state', state_number)

    #Get the relevant state from the file
    state_counter = 0
    while state_counter < state_number + 1:
        newline = logfile.readline()
        splitline = newline.split('|')
        if not newline or splitline[0] == 'RISKRESULT': 
            print('End of logfile reached, state not found!  Only', state_counter, 'states encountered.  State number was', state_number)
            sys.exit()
        if splitline[0] == 'RISKSTATE':
            if state_counter == state_number:
                search_state.from_string(newline, riskboard)
                break
            state_counter += 1

    #Close the logfile
    logfile.close()
    
    #Now plan from source to destination
    run_search(source_territory, destination_territory, search_state)
