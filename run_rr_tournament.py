#Play a complete round robin tournament of a given set of ai's 
import sys
import imp
import risktools
import time
import os
import random
from play_risk_ai import *
from math import factorial as fac

def print_usage():
    print('USAGE: python run_rr_tournament.py ai_1 name_1 ai_2 name_2 . . . a_n name_n num_players match_length (where n is an arbitrary number), num_players is the number of players in a single match, and match_length is the length of each individual match. This should be a multiple of num_players (to fairly alternate who goes first))')

def binomial(x, y):
    try:
        binom = fac(x) // fac(y) // fac(x - y)
    except ValueError:
        binom = 0
    return binom
    
def get_match_names(names, names_per_match):
    match_names = []
    cur_match = []
    get_match_names_d(names, names_per_match, cur_match, match_names,0)
    print('These are the match names: ', match_names)
    return match_names
    
def get_match_names_d(names, names_per_match, cur_match, match_names,i):
    if len(cur_match) == names_per_match:
        new_match = cur_match[:]
        match_names.append(new_match)
        return
    
    for j in range(i,len(names)):
        n = names[j]
        if n not in cur_match:
            cur_match.append(n)
            get_match_names_d(names, names_per_match, cur_match, match_names,j)
            cur_match.remove(n)
     
def save_tournament_stats(tstats, fn, i, ppm):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    #Open the logfile
    logname = 'tournaments\RoundRobin_Tournament_' + timestr + '_' + fn + '_' + str(ppm) + '_' + str(i) + '.txt'
    logfile = open(logname, 'w')
    
    for t in tstats:        
        #logfile.write('*****\n' + str(t.winners) + '\n')
        logfile.write(t.to_string() + '\n')
        
    logfile.close()
    
if __name__ == "__main__":
    #Get ais from command line arguments
    if len(sys.argv) <= 2:
        print_usage()
    
    #Keep all of the player access to ais
    ai_players = dict()
    ai_files = dict()
    player_names = []
  
    #Load the ai's that were passed in
    for i in range(1,len(sys.argv)-2,2):
        gai = imp.new_module("ai")
        filecode = open(sys.argv[i])
        exec filecode in gai.__dict__
        filecode.close()
        
        ai_file = os.path.basename(sys.argv[i])
        ai_file = ai_file[0:-3]
  
        ai_files[sys.argv[i+1]] = ai_file
        player_names.append(sys.argv[i+1])
      
        #Make new player
        ai_players[sys.argv[i+1]] = gai        
    
    players_per_match = int(sys.argv[-2])
    match_length = int(sys.argv[-1])
    print('Playing a ', players_per_match, '-player Round Robin Tournament with matches of length: ', match_length)
    print('There are ', len(player_names), 'players: ', player_names)
    #Get all of the matches
    matches = get_match_names(player_names, players_per_match)

    tournament_stats = []
    
    counter = 0

    for m in matches:
        match_stats = Statistics(m)
            
        play_match(m, ai_players, ai_files, match_stats, match_length, False, False)
                
        tournament_stats.append(match_stats)
        
        save_tournament_stats(tournament_stats, 'Int', counter, players_per_match)
        counter += 1

    print('Tournament is over. Played ', len(matches), ' matches. Each match had ', match_length, 'games')
    
    save_tournament_stats(tournament_stats, 'Final', 0)
    
    print('Done with match.')
    
    
    