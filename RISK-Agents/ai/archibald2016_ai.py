import random
from gui.aihelper import *
from risktools import *
from gui.turbohelper import *
import math
import json
import pickle
from Queue import PriorityQueue

my_id = None
my_generals = None
placement_plan = None
placement_count = None

def get_continent_assign_erg(state, cont_territories, our_id, bonus):
    """
    Return the erg for this territory, focused on conquering something on cont_territories
    """
    num_mine = 0.0
    num_opps = dict()
    num_free = 0.0
    total = float(len(cont_territories))

    for t in cont_territories:
        if state.owners[t] is None:
            num_free += 1.0
        elif state.owners[t] != our_id:
            if state.owners[t] not in num_opps:
                num_opps[state.owners[t]] = 0.0
            num_opps[state.owners[t]] += 1.0
        else:
            num_mine += 1.0

    if num_free == 0:
        return 0.0

    #Compute score for me, then each opponent
    #Continent score is max of these
    erg = bonus * ((num_mine + num_free)/(total*num_free)) 

    for oid, numo in num_opps.iteritems():
        o_gain = bonus * ((numo + num_free)/(total*num_free)) 
        erg = max(erg, o_gain)

    return erg

def conquer_search(fringe, state, cont_t, visited, our_id):
    while len(fringe) > 0:
        cur_t = fringe.pop(0)

        if cur_t not in visited:
            visited.append(cur_t)

        for n in state.board.territories[cur_t].neighbors:
            if n in cont_t and state.owners[n] != our_id and n not in visited:
                fringe.append(n)

def conquerable_troops(state, t, cont_t, our_id):
    """
    Calculate how many enemy troops in this continent can be conquered from territory t
    """
    #BFS from t to see which territories can be conquered, then add them up
    fringe = []
    fringe.append(t)
    visited = []
    conquer_search(fringe, state, cont_t, visited, our_id)
    ct = 0
    for v in visited:
        ct += state.armies[v]

    return ct, len(visited)

def get_territory_defend_erg(state, territory, our_id, num_troops, bonus):
    erg = [0.0]*num_troops

    if isFront(state, territory):
        num_attackers = getNumFoes(state, territory)
        previous_dp = getAttackSuccessDistribution(num_attackers, state.armies[territory])
        for nt in range(num_troops):
            num_defenders = state.armies[territory] + nt + 1
            current_dp = getAttackSuccessDistribution(num_attackers, num_defenders) 
            erg[nt] = (current_dp - previous_dp)*bonus
            previous_dp = current_dp

    return erg

def get_territory_place_erg(state, territory, cont_territories, our_id, num_troops, bonus):
    """
    Return the erg for this territory, focused on conquering something on cont_territories
    """
    #Compute the number of enemy troops in this continent that this territory could conquer
    num_defenders, num_steps = conquerable_troops(state, territory, cont_territories, our_id)

    #print '  Getting territory place ERG for', num_troops, 'troops for', state.board.territories[territory].name, ' which can conquer ', num_defenders

    if num_defenders == 0:
        return get_territory_defend_erg(state, territory, our_id, num_troops, bonus)

    erg = [0.0]*num_troops

    for nt in xrange(num_troops):
        num_attackers = nt + 1 + state.armies[territory] - num_steps
        if num_attackers < 1:
            erg[nt] = 0.0
        else:
            cur_dist = getAttackSuccessDistribution(num_attackers,num_defenders)
            success_prob = sum(cur_dist) - cur_dist[0]
            erg[nt] = success_prob * bonus

    return erg

def get_attack_base(state, dest_territories, our_id, num_troops, bonus):
    """
    Return the erg for attacking these territories, and the attack base territory id
    """
    #Find the best base territory
    best_cost = sum(state.armies)
    best_steps = 0
    best_t = None
    for t in range(len(state.owners)):
        if state.owners[t] == our_id:
            #Get number of enemy troops on path between this territory and dest_territories
            startnode = attackBaseSearchNode(t, None, state, our_id)
            fringe = PriorityQueue()
            fringe.put(startnode)
            visited = []
            goal_node = attackBaseSearch(fringe, dest_territories, visited, best_cost)
            if goal_node is not None:
                if best_t is None or goal_node.cost < best_cost:
                    best_cost = goal_node.cost
                    best_steps = goal_node.steps
                    best_t = t

    #Now compute the expected reinforcement reduction to the enemy
    # for each of the 
    # number of troops added to our base.
    # Assume we lose 1 troop per step of the path for occupying, but
    # Otherwise it is one big battle

    erg = [0.0]*num_troops

    for nt in xrange(num_troops):
        num_attackers = nt + 1 + state.armies[best_t] - best_steps
        num_defenders = best_cost
        if num_attackers < 0:
            erg[nt] = 0.0
        else:
            cur_dist = getAttackSuccessDistribution(num_attackers,num_defenders)
            success_prob = sum(cur_dist) - cur_dist[0]
            erg[nt] = success_prob * bonus

    return erg, best_t

class General():
    def __init__(self, continent, our_id):
        self.name = continent.name
        self.continent = continent
        self.territories = continent.territories
        self.reward = continent.reward
        self.num_territories = len(continent.territories)
        self.id = our_id
        self.placement_plan = None

    def print_status(self, state):
        my_troops = 0
        my_ts = 0
        opp_ts = 0
        opp_troops = 0
        for t in self.territories:
            if state.owners[t] == self.id:
                my_ts += 1
                my_troops += state.armies[t]
            else:
                opp_ts += 1
                opp_troops += state.armies[t]

        print '   General ', self.name, ' ID: ', self.id, 'Status Report: We have ', my_troops, ' in ', my_ts, 'Territories. Enemy has ', opp_troops, 'in', opp_ts, 'territories.' 

    def report_assign_request(self, state):
        """
        Report expected reinforcement gain for assigning a troop to this general
        Return gain and the action that achieves this
        ERG the same for all terrs in this continent.  
        """
        erg = get_continent_assign_erg(state, self.territories, self.id, self.reward)

        #Get action
        actions = getAllowedActions(state)

        c_actions = []
        for a in actions:
            if state.board.territory_to_id[a.to_territory] in self.territories:
                c_actions.append(a)

        if len(c_actions) == 0:
            return 0.0, random.choice(actions)

        return erg, random.choice(c_actions)

    def report_place_request(self, state, num_troops):
        """
        Report expected reinforcement gain per troops for each number of troops
        Come up with a placement plan for any troops we do get, up to the full number
        """
        #print ' General', self.name, ' reporting placement request for', num_troops, ' troops'
        
        best_erg = None
        own_continent = True
        t_ergs = dict()
        self.placement_count = 0 

        for t in self.territories:
            if state.owners[t] == self.id:
                #I own a territory in continent.  Compute erg for it
                t_erg = get_territory_place_erg(state, t, self.territories, self.id, num_troops, self.reward)
                t_ergs[t] = t_erg
                #print '  Getting territory ERG for ', state.board.territories[t].name, ' : ', t_erg
                if best_erg is None or t_erg[-1] > best_erg[-1]:
                    best_erg = t_erg
                    self.placement_plan = [t]*num_troops
            else:
                own_continent = False

        if own_continent:
            self.placement_plan = [0]*num_troops
            placements = dict()
            best_erg = [0.0]*num_troops
            for t in self.territories:
                placements[t] = 0

            for nt in range(num_troops):
                best_current_erg = 0.0
                best_current_t = None

                for ct in self.territories:
                    cur_erg = t_ergs[ct][placements[t]]
                    if best_current_t is None or cur_erg > best_current_erg:
                        best_current_erg = cur_erg
                        best_current_t = ct

                best_erg[nt] = best_current_erg
                placements[best_current_t] += 1
                self.placement_plan[nt] = best_current_t
                print '              We own the continent!  Now defending.'


        if best_erg is None:
            #Find nearest base, we are in attack mode. How many troops do we need?!?!?
            a_erg, attack_base = get_attack_base(state, self.territories, self.id, num_troops, self.reward)
            self.placement_plan = [attack_base]*num_troops
            print '             Continent held by enemy!  Locate Base and prep Attack!'
            return a_erg

        else:
            if not own_continent:
                print '             Continent in question. Report attack placements. '
            #Determine what the best territory to place each number of
            #troops on is
            return best_erg            

    def place(self, state):
        #Place troop on the next place in our placement_plan
        actions = getAllowedActions(state)
        print ' General', self.name, ' placing a troop.  This is placement', self.placement_count
        if self.placement_count < len(self.placement_plan):
            dest_territory = self.placement_plan[self.placement_count]
            self.placement_count += 1
            print '         Destination territory : ', dest_territory, ' : ', state.board.territories[dest_territory].name
            for a in actions:
                if state.board.territory_to_id[a.to_territory] == dest_territory:
                    print '        Chosen action: ', a.to_string()
                    return a
        else:
            return random.choice(actions)

        return random.choice(actions)

    def lead_attack(self, state):
        """
        Return an attack action for this state for this general, or None if there is no attack for this general
        """
        #print ' General ', self.name, ' leading the attack.'
        actions = getAllowedActions(state)
        enemy_territories = []
        for t in self.territories:
            if state.owners[t] != self.id:
                enemy_territories.append(t)

        #print '    There are ', len(enemy_territories), 'enemy territories on my continent'

        for e in enemy_territories:
            #print 'Probing attack on ', state.board.territories[e].name, 'which has ', state.armies[e], 'troops'
            num_defenders = state.armies[e]
            best_t = None
            best_p = 0.40
            #Find the neighbor that has the best chance of beating this dude
            for n in state.board.territories[e].neighbors:
                num_attackers = state.armies[n]
                cur_dist = getAttackSuccessDistribution(num_attackers,num_defenders)
                success_prob = sum(cur_dist) - cur_dist[0]
                #print 'Attack from ', state.board.territories[n].name, '? (with', state.armies[n], ') Success probability : ', success_prob
                #if best_t is None or success_prob > best_p:
                if success_prob > best_p:
                    best_t = n
                    best_p = success_prob
            if best_t is not None:
                for a in actions:
                    if a.to_territory is not None:
                        to_t = state.board.territory_to_id[a.to_territory]
                        from_t = state.board.territory_to_id[a.from_territory]
                        if to_t == e and from_t == best_t:
                            return a

        return None 

    def occupy(self, state):
        """
        Return the best occupy action for this state
        """
        pass

    def report_fortify_delta(self, state):
        """
        Report the expected reinforcement gain per troops for allowing this general to fortify
        and return fortify action associated with it
        """
        pass

def initialize_generals(state, our_id):
    """
    Initialize all of our generals
    """
    global my_generals
    my_generals = []

    #print 'INITIALIZING GENERALS with ID:  ', our_id

    for n, c in state.board.continents.iteritems():
        #print '   General for ', n
        newG = General(c, our_id)
        my_generals.append(newG)

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    global my_id
    global placement_plan

    #if time_left is not None:
        #Decide how much time to spend on this decision

    #Get the possible actions in this state
    actions = getAllowedActions(state)
    
    my_id = state.current_player

    if my_generals is None:
        initialize_generals(state, my_id)   

    for g in my_generals:
        g.id = my_id

    # Handle Each turn type separately
    if state.turn_type == 'PreAssign':
        placement_plan = None
        return pickAssign(state, actions)
  
    if state.turn_type == 'PrePlace':
        placement_plan = None
        if my_id == 0:
            return pickPlaceTAD(state, actions)
        else:
            return pickPlace(state, actions)
        
    if state.turn_type == 'Place':
        return pickPlaceTAD(state, actions)
        
    if state.turn_type == 'TurnInCards':
        placement_plan = None
        return actions[-1]
    
    if state.turn_type == 'Occupy':
        placement_plan = None
        return pickOccupy(state,actions)
    
    if state.turn_type == 'Attack':
        placement_plan = None
        return pickAttack(state, actions)    
    
    if state.turn_type == 'Fortify':
        placement_plan = None
        return pickFortify(state, actions)    
    
def getNumFoes(state, t):
    global my_id
    num_f = 0
    for n in state.board.territories[t].neighbors:
        if state.owners[n] != my_id:
            num_f += state.armies[n]
    return num_f
  
def pickAttack(state, actions):
#Attack first territory that we don't have in continent list, as long as we have at least 4 guys on it
    for g in my_generals:
        a = g.lead_attack(state)
        if a is not None:
            return a

    return actions[-1]

attackSuccessDistribution = None

def getAttackSuccessDistribution(num_attackers, num_defenders):
    """
    Return probability of each outcome (number of attackers left) (not including one you can't attack with)
    """
    global attackSuccessDistribution

    num_attackers -= 1

    #print 'gASD for ', num_attackers, 'attackers and ', num_defenders, 'defenders'
    size_limit = 29
    if attackSuccessDistribution is None:
        f = open('attack_success_probs.pkl')
        attackSuccessDistribution = pickle.load(f)
        f.close()

    if num_attackers > size_limit:
        num_attackers = size_limit
    if num_defenders > size_limit:
        num_defenders = size_limit

    entry = str(num_attackers) + '.' + str(num_defenders)
    if entry in attackSuccessDistribution:
        #print 'gASD entry is ', entry, attackSuccessDistribution[entry]
        return attackSuccessDistribution[entry]
    else:
        return [0.0]


def getContinentBonusDelta(state, tid):
    for cn,c in state.board.continents.iteritems():
        for t in c.territories:
            if t == tid:
                bonus = c.reward
                myt = 0
                oppt = 0
                for tt in c.territories:
                    if state.owners[tt] != my_id:
                        oppt += 1
                    else:
                        myt += 1
                return bonus * ((1/float(myt+1)) + (1/float(oppt)))
    print 'ERROR in CONTINENT BONUS DELTA'


def getNeighborAttackDelta(state, tid, nid):
    na = state.armies[tid]
    nd = state.armies[nid]
    #Get probability distribution
    cur_dist = getAttackSuccessDistribution(na,nd)
    pos_dist = getAttackSuccessDistribution(na + 1, nd)

    cur_wp = sum(cur_dist) - cur_dist[0]
    pos_wp = sum(pos_dist) - pos_dist[0]

    delta = pos_wp - cur_wp

    cb = getContinentBonusDelta(state, nid)

    return delta * cb

def getTerritoryAttackDelta(state, territory_id):
    #For each neighbor of this territory
    for n in state.board.territories[territory_id].neighbors:
        max_nad = None
        if state.owners[n] != my_id:
            nad = getNeighborAttackDelta(state, territory_id, n)
            if max_nad is None or nad > max_nad:
                max_nad = nad
    if max_nad is None:
        max_nad = 0.0
    return max_nad

def pickPlaceTAD(state, actions):
    tads = []

    front_actions = []
    for a in actions:
        if isFront(state, state.board.territory_to_id[a.to_territory]):
            front_actions.append(a)

    if len(front_actions) == 0:
        print 'NO FRONTS???!?1?!?'
        return random.choice(actions)

    for ai in range(len(front_actions)):
        tads.append(getTerritoryAttackDelta(state, state.board.territory_to_id[front_actions[ai].to_territory]))

    return select_action_by_probability(tads, front_actions)

def get_territory_vulnerability(state, t):
    foes = getNumFoes(state, t)
    friends = state.armies[t]
    v_d = getAttackSuccessDistribution(foes, friends)
    vulnerability = sum(v_d) - v_d[0]
    return vulnerability


def select_action_by_probability(my_vs, actions):
    total_v = sum(my_vs)

    sv = random.uniform(0,total_v)

    cv = 0
    vi = 0
    while cv < sv:
        cv += my_vs[vi]
        vi += 1

    if vi > len(actions):
        print 'ERROR IN SELECT ACTION BY VULNERABILTIY'
        return random.choice(actions)

    return actions[vi-1]

def pickPlace(state, actions):
    my_vs = []

    for ai in range(len(actions)):
        my_vs.append(get_territory_vulnerability(state,state.board.territory_to_id[actions[ai].to_territory]))

    return select_action_by_probability(my_vs, actions)

def pickPlaceDefense(state, actions):
    for a in actions:
        if state.armies[state.board.territory_to_id[a.to_territory]] < 2:
            return a

    return random.choice(actions)

def getFront(state, t):
    front = []
    pid = state.owners[t]
    
    for n in state.board.territories[t].neighbors:
        if state.owners[n] != pid:
            if n not in front:
                front.append(n)

    return front
    
def isFront(state, t):
    pid = state.owners[t]

    for n in state.board.territories[t].neighbors:
        if state.owners[n] != pid:
            return True

    return False
    
def pickFortify(state, actions):
    max_a = None
    max_front = 0
    for a in actions:
        if a.to_territory != None:
            t = state.board.territory_to_id[a.to_territory]
        
            if isFront(state,t):
                mf = getNumFoes(state,t)
                if mf > max_front:
                    max_a = a
                    max_front = mf
                
    if max_a != None:
        return max_a
        
    return random.choice(actions)
    
def pickOccupy(state, actions):
    max_troops = 0
    best_a = actions[0]

    to_front = isFront(state, state.board.territory_to_id[best_a.to_territory])
    from_front = isFront(state, state.board.territory_to_id[best_a.from_territory])
    total_troops = state.armies[state.board.territory_to_id[best_a.from_territory]]
    target_troops = int(total_troops / 2)
    
    if not(to_front and from_front):
        if to_front:
            target_troops = total_troops
        if from_front:
            target_troops = 0
    else:
        to_foes = getNumFoes(state, state.board.territory_to_id[best_a.to_territory])
        from_foes = getNumFoes(state, state.board.territory_to_id[best_a.from_territory])

        target_troops = int(total_troops * to_foes / from_foes)

    best_diff = total_troops + 100
    for a in actions:
        cur_diff = abs(a.troops - target_troops)

        if cur_diff < best_diff:
            best_diff = cur_diff
            best_a = a
    return best_a
    
    
def pickAssign(state, actions):
    av = None
    aa = None
    for g in my_generals:
        v, a = g.report_assign_request(state)
        if aa is None or av < v:
            av = v
            aa = a

    return aa

class attackBaseSearchNode():
    def __init__(self, t_id, parent, state, pid):
        self.id = t_id
        self.parent = parent
        self.cost = state.armies[t_id]
        self.steps = 0
        if parent is not None:
            self.cost = parent.cost + state.armies[t_id]
            self.steps = parent.steps + 1
        self.pid = pid
        self.state = state

    def __lt__(self, other):
        return self.cost < other.cost


def attackBaseSearch(fringe, endset, visited, maximum_allowed_cost):
    while not fringe.empty():

        cur_state = fringe.get()

        if cur_state.cost > maximum_allowed_cost:
            continue

        visited.append(cur_state.id)

        if cur_state.id in endset:
            return cur_state
        else:
            for m in cur_state.state.board.territories[cur_state.id].neighbors:
                if cur_state.state.owners[m] != cur_state.pid and m not in visited:
                    new_state = attackBaseSearchNode(m, cur_state, cur_state.state, cur_state.pid)
                    fringe.put(new_state)
    return None

#Stuff below this is just to interface with Risk.pyw GUI version
#DO NOT MODIFY
    
def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
    print 'AI Wrapper created state. . . '
    game_state.print_state()
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

  