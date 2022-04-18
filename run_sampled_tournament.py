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
    print('USAGE: python run_sampled_tournament.py ai_1 name_1 ai_2 name_2 . . . a_n name_n num_players match_length tournament_length (where n is an arbitrary number), num_players is the number of players in a single match, and match_length is the length of each individual match, which should be a multiple of num_players (to fairly alternate who goes first)) tournament_length tells how many matches to hold as part of the tournament')

class TotalStatistics():
    def __init__(self, player_names):
        self.results = dict()
        for p in player_names:
            self.results[p] = [0.0,0.0]
        
    def print_stats(self):
        print self.to_string()
        
    def add_match_stats(self, stats):
        for p,w in stats.winners.iteritems():
            if p not in self.results:
                print('TOURNAMENT STATS ERROR: player', p, 'not in tournament!')
                return
            r = self.results[p]
            r[0] += stats.games_played
            r[1] += w
                
    def to_string(self):
        output = 'Sampled Tournament Results:\n'
        for p,r in self.results.iteritems():
            if r[0] > 0:
                output += '  ' + p + ' : ' + str( float(r[1]) / float(r[0])) + ' wins per game. (' + str(r[1]) + ' wins in ' + str(r[0]) + ' games)\n'
            else:
                output += '  ' + p + ' : hasn\'t played yet\n'
        return output 
        
    def save_stats(self,fn):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        #Open the logfile
        logname = 'tournaments\Sampled_Tournament_' + timestr + '_' + fn + '.txt'
        logfile = open(logname, 'w')
        logfile.write(self.to_string())
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
    for i in range(1,len(sys.argv)-3,2):
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
    
    players_per_match = int(sys.argv[-3])
    match_length = int(sys.argv[-2])
    tournament_length = int(sys.argv[-1])
    print('Playing a ', players_per_match, '-player sampled Tournament with matches of length: ', match_length)
    print('There are ', len(player_names), 'players: ', player_names)
    #Get all of the matches
    
    tournament_stats = TotalStatistics(player_names)
    
    for i in range(tournament_length):
        m = random.sample(player_names, players_per_match)
        match_stats = Statistics(m)
            
        play_match(m, ai_players, ai_files, match_stats, match_length, False, False)
                
        tournament_stats.add_match_stats(match_stats)
        
        tournament_stats.save_stats('Int')
       
    print('Tournament is over. Played ', tournament_length, ' matches. Each match had ', match_length, 'games')
    
    tournament_stats.save_stats('FINAL')
    tournament_stats.print_stats()
    
    print('Done with match.')
    
    
    