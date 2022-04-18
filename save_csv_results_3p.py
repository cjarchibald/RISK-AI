import sys
import operator

def print_usage():
    print('USAGE: python save_csv_results_3p.py TOURNAMENT_RESULTS_FILE')


def save_line(main_agent, line_agent, agents, winnings, of):
    of.write(line_agent + ',')
    for a in agents:
        if a != main_agent:
            if a == line_agent:
                of.write(',')

            for nss, s in winnings.iteritems():
                ns = nss.split('.')
                if ns[0] == main_agent:
                    if ns[1] == line_agent:
                        if ns[2] == a:
                            of.write(str(s) + ',')
                    if ns[2] == line_agent:
                        if ns[1] == a:
                            of.write(str(s) + ',')


def save_winnings(agents, winnings, apm, filename):
    for a in agents:
        win_fname = filename[:-4] + '_' + a + '.csv'
        win_file = open(win_fname, 'w')

        for aa in agents:
            if aa != a:
                win_file.write(',')
                win_file.write(str(aa))

        win_file.write('\n')

        for aaa in agents:
            if aaa != a:
                save_line(a, aaa, agents, winnings, win_file)
                win_file.write('\n')

        win_file.close()

    print('Done saving winnings. ')


if __name__ == "__main__":


    if len(sys.argv) != 2 :
        print_usage()
    
    agents = []

    winnings = dict()

    agents_per_match = None

    results_file = open(sys.argv[1], 'r')
    for line in results_file:
        det_line = line.split(':')
        if det_line[0].strip() == "WINNERS":
            name_part = line.split('{')
            name_scores = name_part[1].split(',')
            name_scores[-1] = name_scores[-1][:-2]
            names = []
            scores = []

            for ns in name_scores:
                name_s, score_s = ns.split(':')
                name = name_s.strip()[1:-1]
                score = float(score_s.strip())
                names.append(name)
                scores.append(score)
                if name not in agents:
                    agents.append(name)

            if agents_per_match is not None and agents_per_match != len(names):
                print('IRREGULAR NUMBER OF AGENTS PER MATCH')

            agents_per_match = len(names)

            print('NAMES: ', names)

            for ni in range(len(names)):
                n = names[ni]
                onames = []
                for oi in range(len(names)):
                    if oi != ni:
                        onames.append(names[oi])
                print('  OPPONENT NAMES:', onames)
                match_name = n
                for on in onames:
                    match_name = match_name + '.' + on
                print('  Match name: ', match_name)
                winnings[match_name] = scores[ni]

    results_file.close()
    save_winnings(agents, winnings, agents_per_match, sys.argv[1])
