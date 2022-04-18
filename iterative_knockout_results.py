import sys
import operator

def print_usage():
    print('USAGE: python iterative_knockout_results.py TOURNAMENT_RESULTS_FILE')

def print_winnings(winnings, apm):
    sorted_winnings = sorted(winnings.items(), key=operator.itemgetter(1), reverse=True)
    win_sum = 0.0
    print('ORDERED WINNINGS FOR TOP', len(winnings), ' TEAMS : ')
    for sw in sorted_winnings:
        print(sw[0], ' : ', sw[1])
        win_sum += sw[1]
    print('  Win Sum = ', win_sum)
    print('  ')
    done = False
    if len(sorted_winnings) == apm:
        done = True

    return sorted_winnings[-1][0], done

if __name__ == "__main__":


    if len(sys.argv) != 2 :
        print_usage()
    

    
    exclude = []
    done = False

    while not done:

        winnings = dict()

        agents_per_match = None

        results_file = open(sys.argv[1], 'r')
        for line in results_file:
            det_line = line.split(':')
            if det_line[0].strip() == "WINNERS":
                name_part = line.split('{')
                name_scores = name_part[1].split(',')
                name_scores[-1] = name_scores[-1][:-2]
                nmscore = dict()
                for ns in name_scores:
                    #print 'NAME SCORE: ', ns
                    name_s, score_s = ns.split(':')
                    name = name_s.strip()[1:-1]
                    score = float(score_s.strip())
                    #print 'FINALIZED NAME AND SCORE: ', name, ' and ', score
                    nmscore[name] = score

                if agents_per_match is not None and agents_per_match != len(nmscore):
                    print('IRREGULAR NUMBER OF AGENTS PER MATCH')

                agents_per_match = len(nmscore)


                include_match = True
                for e in exclude:
                    if e in nmscore:
                        include_match = False

                if include_match:
                    for n,s, in nmscore.iteritems():        
                        if n in winnings: 
                            winnings[n] += s
                        else:
                            winnings[n] = s

        results_file.close()
        last_place, done = print_winnings(winnings, agents_per_match)
        exclude.append(last_place)
