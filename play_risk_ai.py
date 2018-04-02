# Play some ai's against each other in a game
import sys
import imp
import risktools
import time
import os
import random


def print_usage():
    print 'USAGE: python play_risk_ai.py ai_1 name_1 ai_2 name_2 . . . a_n name_n match_length (where n is 7 or less, and match_length should be a multiple of n (to fairly alternate who goes first))'


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
        print 'MATCH STATISTICS'
        print 'GAMES PLAYED : ', self.games_played
        print 'NORMAL WINS  : ', self.wins
        print 'TIES         : ', self.ties
        print 'TIME OUTS    : ', self.time_outs
        print 'WINNERS      : ', self.winners
        print 'AVERAGE TURNS: ', float(
            self.total_turns) / float(self.games_played)


def play_game(player_names, ai_players, ai_files, stats, verbose=False):

    # Set up the board
    board = risktools.loadBoard("world.zip")

    time_left = dict()

    logdir = 'matches/'
    logname = 'RISKTOURNAMENT'

    action_limit = 5000  # total between players
    player_time_limit = 600  # seconds per player

    # Create the players
    for name in player_names:
        # Make new player
        time_left[name] = player_time_limit
        #logname = logname + '_' + ai_files[name] + '_' + name
        ap = risktools.RiskPlayer(name, len(board.players), 0, False)
        board.add_player(ap)

    # Get initial game state
    state = risktools.getInitialState(board)

    action_count = 0
    turn_count = 0
    done = False
    last_player_name = None

    timestr = time.strftime("%Y%m%d-%H%M%S")
    # Open the logfile
    logname = logname + '_' + str(stats.games_played) + '_' + timestr + '.log'
    logfile = open(logdir + logname, 'w')

    logfile.write(board.to_string())
    logfile.write('\n')

    final_string = ''

    print 'Players order for game: ', player_names

    # Play the game
    while not done:
        if verbose:
            print '--*TURN', action_count, 'BEGIN*--'
            print 'CURRENT PLAYER: ', state.players[state.current_player].name
            print 'TURN-TYPE: ', state.turn_type
            print 'TIME-LEFT: ', time_left[state.players[state.current_player].name]

        # Log the current state
        logfile.write(state.to_string())
        logfile.write('\n')

        # Get current player
        current_ai = ai_players[state.players[state.current_player].name]

        # Make a copy of the state to pass to the other player
        ai_state = state.copy_state()

        # Start timer
        start_action = time.clock()

        # print 'STATE BEFORE : ', state.print_state()
        current_player_name = state.players[state.current_player].name
        error_actions = risktools.getAllowedActions(state)
        current_action = random.choice(error_actions)

        # Ask the current player what to do
        try:
            current_action = current_ai.getAction(
                ai_state, time_left[state.players[state.current_player].name])
        except:
            # Catch errors and count this as a loss for the player
            time_left[current_player_name] = -1.0
            print 'There was an error for player: ', current_player_name, '  THEY LOSE!'

        # print 'ACTION CHOSEN : ', current_action.print_action()

        if current_player_name != last_player_name:
            turn_count += 1
            last_player_name = current_player_name

        # Stop timer
        end_action = time.clock()

        # Determine time taken and deduct from player's time left
        action_length = end_action - start_action
        time_left[current_player_name] = time_left[current_player_name] - action_length
        current_time_left = time_left[current_player_name]

        if verbose:
            print 'IN ', action_length, ' SECONDS CHOSE ACTION: ', current_action.description()

        # Execute the action on the master game state
        new_states, new_state_probabilities = risktools.simulateAction(
            state, current_action)

        # See if there is randomness in which state we go to next
        if len(new_states) > 1:
            # Randomly pick one according to probabilities
            state = select_state_by_probs(new_states, new_state_probabilities)
        else:
            state = new_states[0]

        logfile.write(current_action.to_string())
        logfile.write('\n')

        if state.turn_type == 'GameOver' or action_count > action_limit or current_time_left < 0:
            done = True
            # Get other player name
            other_player_names = []
            for p in player_names:
                if p != current_player_name:
                    other_player_names.append(p)

            if state.turn_type == 'GameOver':
                print 'Game is over.', current_player_name, ' is the winner.'
                final_string = "RISKRESULT|" + current_player_name + ",1|"
                for opn in other_player_names:
                    final_string = final_string + opn + ",0|"
                final_string = final_string + 'Game End'
                stats.winners[current_player_name] += 1
                stats.wins += 1
            if action_count > action_limit:
                print 'Action limit exceeded.  Game ends in a tie'
                final_string = "RISKRESULT|" + current_player_name + ",0.5|"
                for opn in other_player_names:
                    final_string = final_string + opn + ",0.5|"
                final_string = final_string + 'Action Limit Reached'
                stats.winners[current_player_name] += (
                    1.0 / float(len(other_player_names) + 1))
                for opn in other_player_names:
                    stats.winners[opn] += (1.0 /
                                           float(len(other_player_names) + 1))
                stats.ties += 1
            if current_time_left < 0:
                print 'Agent time limit exceeded. ', current_player_name, ' loses by time-out.'
                final_string = "RISKRESULT|" + current_player_name + ",0|"
                for opn in other_player_names:
                    final_string = final_string + opn + ",1|"
                    stats.winners[opn] += (1.0 /
                                           float(len(other_player_names)))
                final_string = final_string + 'Time Out'
                stats.time_outs += 1

        action_count = action_count + 1
        if verbose:
            print '--*TURN END*--'

    # Update stats
    stats.total_turns += turn_count
    stats.games_played += 1
    final_string = final_string + '|Turn Count = ' + str(turn_count)
    if verbose:
        print ' Final State at end of game:'
        state.print_state()
    print final_string
    print 'Game log saved to: ', logname
    logfile.write(state.to_string())
    logfile.write('\n')
    logfile.write(final_string)
    logfile.write('\n')
    logfile.close()
    # stats.print_stats()


if __name__ == "__main__":
    # Get ais from command line arguments
    if len(sys.argv) <= 2:
        print_usage()

    # Keep all of the player access to ais
    ai_players = dict()
    ai_files = dict()
    player_names = []

    # Load the ai's that were passed in
    for i in range(1, len(sys.argv)-1, 2):
        gai = imp.new_module("ai")
        filecode = open(sys.argv[i])
        exec filecode in gai.__dict__
        filecode.close()

        ai_file = os.path.basename(sys.argv[i])
        ai_file = ai_file[0:-3]

        ai_files[sys.argv[i+1]] = ai_file
        player_names.append(sys.argv[i+1])

        # Make new player
        ai_players[sys.argv[i+1]] = gai

    stats = Statistics(player_names)
    match_length = int(sys.argv[-1])
    print 'Playing match of length: ', match_length

    for i in range(match_length):
        # REORDER PLAYERS FOR THIS GAME
        temp_names = player_names[1:]
        temp_names.append(player_names[0])
        player_names = temp_names

        print 'PLAYING GAME', i, 'OF', match_length, 'LENGTH MATCH'
        play_game(player_names, ai_players, ai_files, stats)

    print 'MATCH IS OVER.  PLAYED', match_length, 'GAMES'
    stats.print_stats()

    print 'Done with match.'
