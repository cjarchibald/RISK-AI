#Play some AI's against each other in a game of RISK
import sys
import imp
import risktools
import time
import os
import argparse
import random
import traceback

def parse_args():
    parser = argparse.ArgumentParser(description='Play a RISK match between some AIs')
    parser.add_argument("ais",type = str, nargs = '+', help="List of the AIs for match: ai_1 name_1 ai_2 name_2 . . .")
    parser.add_argument("-n, --num", dest='num', type = int, help = "Specify the number of games each player goes first in match", default = 5)
    parser.add_argument("-w, --write", dest='save', action='store_true', help = "Indicate that logfiles for games in the match should be saved to the logs directory", default = False)
    parser.add_argument("-v, --verbose", dest='verbose', action='store_true', help = "Indicate that the match should be run in verbose mode", default = False)
    return parser.parse_args()

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
   
def is_valid_action(state, action):
    action_string = action.to_string()
    actions = risktools.getAllowedActions(state)
    for a in actions:
        astring = a.to_string()
        if astring == action_string:
            return True
    return False

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
        print('MATCH STATISTICS:')
        print('  GAMES PLAYED : ', self.games_played)
        print('  NORMAL WINS  : ', self.wins)
        print('  TIES         : ', self.ties)
        print('  TIME OUTS    : ', self.time_outs)
        print('  WINNERS      : ', self.winners)
        print('  AVERAGE TURNS: ', float(self.total_turns) / float(self.games_played))
    
def play_game(player_names, ai_players, ai_files, stats, save_logfile, verbose=False):
    """
    This will actually play a single game between the players given
    """
    #Set up the board
    board = risktools.loadBoard("world.zip")
    
    time_left = dict()
    
    logname = 'logs' + os.path.sep + 'RISKGAME'
    
    action_limit = 5000 #total between players  MODIFY IF USING DIFFERENT LENGTH
    player_time_limit = 600 #seconds per player MODIFY IF USING DIFFERENT LENGTH
    
    #Create the players
    for name in player_names:
        #Make new player
        time_left[name] = player_time_limit

        #Add players name to logfile name
        logname = logname + '_' +  name
        ap = risktools.RiskPlayer(name, len(board.players), 0, False)
        board.add_player(ap)
        
    #Get initial game state
    state = risktools.getInitialState(board)
    
    action_count = 0
    turn_count = 0
    done = False
    last_player_name = None
    
    if save_logfile: 
        timestr = time.strftime("%Y%m%d-%H%M%S")
        #Open the logfile
        logname = logname + '_' + str(stats.games_played) + '_' + timestr + '.log'
        logfile = open(logname, 'w')
        
        logfile.write(board.to_string())
        logfile.write('\n')
    
        final_string = ''
    
    print('Players order for game: ', player_names)
    
    #Play the game
    while not done:
        if verbose:
            print('--*TURN', action_count, 'BEGIN*--')
            print('CURRENT PLAYER: ', state.players[state.current_player].name)
            print('TURN-TYPE: ', state.turn_type)
            print('TIME-LEFT: ', time_left[state.players[state.current_player].name])
        
        if save_logfile:
            #Log the current state
            logfile.write(state.to_string())
            logfile.write('\n')

        #Get current player
        current_ai = ai_players[state.players[state.current_player].name]
        
        #Make a copy of the state to pass to the other player
        ai_state = state.copy_state()

        #Start timer
        start_action = time.perf_counter()
        
        #Get current player name
        current_player_name = state.players[state.current_player].name

        #Get an action in case they crash (allows following code to run until we end the game)
        error_actions = risktools.getAllowedActions(state)
        current_action = random.choice(error_actions)
        
        # Ask the current player what to do
        try:
            current_action = current_ai.getAction(ai_state, time_left[state.players[state.current_player].name])
        except Exception as e:
            # Catch errors and count this as a loss for the player
            # Print error information
            print('There was an error for player: ', current_player_name, '  THEY LOSE!')
            print(' ERROR INFORMATION: ')
            print(e)
            traceback.print_exc()
            time_left[current_player_name] = -1.0
            
        
        if not is_valid_action(state, current_action):
            print('Player selected invalid action.  ERROR, THEY LOSE!')
            print('  Action selected: ', current_action.to_string())
            print('  Possible valid actions: ')
            for ea in error_actions:
                print('   ', ea.to_string())
            current_action = random.choice(error_actions)
            time_left[current_player_name] = -1.0
        
        #Keep track of turns (when the player changes)
        if current_player_name != last_player_name:
            turn_count += 1                   
            last_player_name = current_player_name

        #Stop timer
        end_action = time.perf_counter()
        
        #Determine time taken and deduct from player's time left
        action_length = end_action - start_action
        time_left[current_player_name] = time_left[current_player_name] - action_length
        current_time_left = time_left[current_player_name]
       
        if verbose:
            print('IN ', action_length, ' SECONDS CHOSE ACTION: ', current_action.description())
        
        #Execute the action on the master game state
        new_states, new_state_probabilities = risktools.simulateAction(state, current_action)

        #See if there is randomness in which state we go to next
        if len(new_states) > 1:
            #Randomly pick one according to probabilities
            state = select_state_by_probs(new_states, new_state_probabilities)
        else:
            state = new_states[0]

        if save_logfile:
            logfile.write(current_action.to_string())
            logfile.write('\n')
        
        if state.turn_type == 'GameOver' or action_count > action_limit or current_time_left < 0:
            done = True

            #Get other player name
            other_player_names = []
            for p in player_names:
                if p != current_player_name:
                    other_player_names.append(p)
                
            #See if the game is over    
            if state.turn_type == 'GameOver':
                print('Game is over.', current_player_name, ' is the winner.')
                final_string = "RISKRESULT|" + current_player_name + ",1|"
                for opn in other_player_names:
                    final_string = final_string + opn + ",0|"
                final_string = final_string + 'Game End'
                stats.winners[current_player_name] += 1
                stats.wins += 1

            #See if we have exceeded the action count
            if action_count > action_limit:
                print('Action limit exceeded.  Game ends in a tie')
                tie_score = round((1.0 / float(len(other_player_names) + 1)), 2)
                final_string = "RISKRESULT|" + current_player_name + "," + str(tie_score) + "|"
                for opn in other_player_names:
                    final_string = final_string + opn + "," + str(tie_score) + "|"
                final_string = final_string + 'Action Limit Reached'
                stats.winners[current_player_name] += tie_score
                for opn in other_player_names:
                    stats.winners[opn] += tie_score
                stats.ties += 1

            #See if the agent timed out
            if current_time_left < 0:
                print('Agent time limit exceeded. ', current_player_name, ' loses by time-out.')
                final_string = "RISKRESULT|" + current_player_name + ",0|"
                time_out_score = round((1.0 / float(len(other_player_names))), 2)
                for opn in other_player_names:
                    final_string = final_string + opn + "," + str(time_out_score) + "|"
                    stats.winners[opn] += time_out_score
                final_string = final_string + 'Time Out'
                stats.time_outs += 1
        
        action_count = action_count + 1
        if verbose:
            print('--*TURN END*--')
        
    #Update stats
    stats.total_turns += turn_count
    stats.games_played += 1
    final_string = final_string + '|Turn Count = ' + str(turn_count)
    if verbose:
        print(' Final State at end of game:')
        state.print_state()
    print(final_string)
    if save_logfile:
        print('Game log saved to: ', logname)
        logfile.write(state.to_string())
        logfile.write('\n')
        logfile.write(final_string)
        logfile.write('\n')
        logfile.close()    

def play_match(player_names, ai_players, ai_files, stats, games_per_agent, save_logfile, verbose):
    """
    Play a match between the given AIs
    """    
    match_length = games_per_agent * len(player_names)
    print('Playing match of length: ', match_length)


    for i in range(match_length):
    
        #Randomize the player order before each cycle of games
        if (i % len(player_names) == 0):
            random.shuffle(player_names)
            print('Randomizing player names')
            
        #Cycle through the player order for this set
        temp_names = player_names[1:]
        temp_names.append(player_names[0])
        player_names = temp_names
        
        print('PLAYING GAME', i, 'OF', match_length, 'LENGTH MATCH :', player_names)
        play_game(player_names, ai_players, ai_files, stats, save_logfile, verbose)
        
    print('\n*******************************\nMATCH IS OVER.  PLAYED', match_length, 'GAMES\n*******************************\n')
    stats.print_stats()

if __name__ == "__main__":
    
    #Parse command line arguments    
    args = parse_args()

    #Keep all of the player access to ais
    ai_players = dict()
    ai_files = dict()
    player_names = []
  
    #Load the ai's that were passed in
    for i in range(0,len(args.ais)-1,2):
        gai = imp.new_module("ai")
        filecode = open(args.ais[i])
        exec(filecode.read(), gai.__dict__)
        filecode.close()
        
        ai_file = os.path.basename(args.ais[i])
        ai_file = ai_file[0:-3]
  
        ai_files[args.ais[i+1]] = ai_file
        player_names.append(args.ais[i+1])
      
        #Make new player
        ai_players[args.ais[i+1]] = gai
    
    #Create the stats object    
    stats = Statistics(player_names)

    #Actually play the match
    play_match(player_names, ai_players, ai_files, stats, args.num, args.save, args.verbose)

    
    