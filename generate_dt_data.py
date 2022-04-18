import sys
import imp
import risktools
import time
import os
import random
import json

###### generate_dt_data.py
#      This scripte will generate data for learning decision trees
#      It will do this by playing a match between two specified agents
######

def print_usage():
    print('USAGE: python generate_dt_data.py ai_1 name_1 ai_2 name_2 match_length')
    
def select_state_by_probs(states, probs):
    if len(states) == 1:
        return states[0]

    r = random.random()
    i = 0
    prob_sum = probs[0]
    while prob_sum < r:
        i += 1
        prob_sum += probs[i]
    return states[i]
   
class Statistics():
    def __init__(self, player_names):
        self.games_played = 0
        self.winners = dict()
        for n in player_names:
            self.winners[n] = 0
            
        self.total_turns = 0
        self.wins = 0
        self.ties = 0
        self.time_outs = 0
        
    def print_stats(self):
        print('MATCH STATISTICS')
        print('GAMES PLAYED : ', self.games_played)
        print('NORMAL WINS  : ', self.wins)
        print('TIES         : ', self.ties)
        print('TIME OUTS    : ', self.time_outs)
        print('WINNERS      : ', self.winners)
        print('AVERAGE TURNS: ', float(self.total_turns) / float(self.games_played))
    
def play_game(player_names, ai_players, ai_files, stats, logfile, verbose=False):

    #Set up the board
    board = risktools.loadBoard("world.zip")
    
    time_left = dict()
    
    saved_start_state = False
    
    action_limit = 5000 #total between players
    player_time_limit = 600 #seconds per player
    
    #Create the players
    for name in player_names:
        #Make new player
        time_left[name] = player_time_limit

        ap = risktools.RiskPlayer(name, len(board.players), 0, False)
        board.add_player(ap)
        
    #Get initial game state
    state = risktools.getInitialState(board)

    starting_state = None
    
    action_count = 0
    turn_count = 0
    done = False
    last_player_name = None
    
    #Play the game
    while not done:
        if starting_state is None and None not in state.owners:
            starting_state = state.copy_state()
        
        #Get current player
        current_ai = ai_players[state.players[state.current_player].name]
        
        #Make a copy of the state to pass to the other player
        ai_state = state.copy_state()

        #Start timer
        start_action = time.clock()
        
        #Ask the current player what to do
        current_action = current_ai.getAction(ai_state, time_left[state.players[state.current_player].name])
        current_player_name = state.players[state.current_player].name
        
        if current_player_name != last_player_name:
            turn_count += 1
                   
            last_player_name = current_player_name

        #Stop timer
        end_action = time.clock()
        
        #Determine time taken and deduct from player's time left
        action_length = end_action - start_action
        time_left[state.players[state.current_player].name] = time_left[state.players[state.current_player].name] - action_length
        current_time_left = time_left[state.players[state.current_player].name]

        #Execute the action on the master game state
        new_states, new_state_probabilities = risktools.simulateAction(state, current_action)

        #See if there is randomness in which state we go to next
        if len(new_states) > 1:
            #Randomly pick one according to probabilities
            state = select_state_by_probs(new_states, new_state_probabilities)
        else:
            state = new_states[0]
        
        if state.turn_type == 'GameOver' or action_count > action_limit or current_time_left < 0:
            done = True
            #Get other player name
            other_player_names = []
            for p in player_names:
                if p != current_player_name:
                    other_player_names.append(p)
                    
            if state.turn_type == 'GameOver':
                stats.winners[current_player_name] += 1
                stats.wins += 1
            if action_count > action_limit:
                stats.winners[current_player_name] += 0.5
                for opn in other_player_names:
                    stats.winners[opn] += 0.5
                stats.ties += 1
            if current_time_left < 0:
                stats.winners[other_player_name] += 1
                stats.time_outs += 1
        
        action_count = action_count + 1

    #Update stats
    stats.total_turns += turn_count
    stats.games_played += 1
    
    write_datum(starting_state, stats, logfile)
    
def write_header(logfile):
    territory_names = ['HasFirstTurn']
    #Get the board
    board = risktools.loadBoard("world.zip")
    for t in board.territories:
        territory_names.append(t.name)
    
    logfile.write(json.dumps(territory_names))
    logfile.write('\n')
    
def write_datum(state, stats, logfile):
    for p in state.board.players:
        features = []
        if state.current_player == p.id:
            features.append(1)
        else:
            features.append(0)
        for t in state.owners:
            if t == p.id:
                features.append(1)
            else:
                features.append(0)
    
        utility = stats.winners[p.name]
        
        logfile.write(json.dumps(features) + '|' + json.dumps(utility))
        logfile.write('\n')
    
    
if __name__ == "__main__":
    #Get ais from command line arguments
    if len(sys.argv) <= 2:
        print_usage()
    
    #Keep all of the player access to ais
    ai_players = dict()
    ai_files = dict()
    player_names = []
    match_length = int(sys.argv[-1])    
    logname = 'dt_data\Dataset_' + str(match_length)

    
    #Load the ai's that were passed in
    for i in range(1,len(sys.argv)-1,2):
        gai = imp.new_module("ai")
        filecode = open(sys.argv[i])
        exec filecode in gai.__dict__
        filecode.close()
        
        ai_file = os.path.basename(sys.argv[i])
        ai_file = ai_file[0:-3]
  
        ai_files[sys.argv[i+1]] = ai_file
        player_names.append(sys.argv[i+1])
        logname = logname + '_' + ai_file + '_' + sys.argv[i+1]
        #Make new player
        ai_players[sys.argv[i+1]] = gai
        
    
    
    print('Playing match of length: ', match_length)
  
    timestr = time.strftime("%Y%m%d-%H%M%S")
    #Open the logfile
    logname = logname + '_' + timestr + '.dat'
    logfile = open(logname, 'w')    
    
    write_header(logfile)
    
    for i in range(match_length):
        #REORDER PLAYERS FOR THIS GAME
        temp_names = player_names[1:]
        temp_names.append(player_names[0])
        player_names = temp_names
        stats = Statistics(player_names)
        if i % 100 == 0:
            print('Generating datum ', i, 'OF', match_length)
        play_game(player_names, ai_players, ai_files, stats, logfile)
        
    logfile.close()
    print('Data generated.', match_length, ' data points generated.')
    
    
    