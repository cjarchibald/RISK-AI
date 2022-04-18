README FOR RISK SOFTWARE

**************************
Brief Introduction to RISK
**************************
The game of risks consists of multiple (2-8) players competing for territory on a map of the world.  
There are several different phases of the game, and different decisions that must be made. 

** PREGAME ** 
In the pregame the different players select territories and place their initial troops on the board. 
The turn types that occur during this stage are: 
1. PreAssign - players select a territory that does not have an owner.  This will place a single troop in that territory. 
2. PrePlace - once all of the territories have an owner, the players place their remaining troops on one of the territories that they own.  This will place a single troop on a selected territory. 

Once all of the initial troops have been placed on the board we enter the main phase of the game. 

** MAIN GAME **
In the main phase of the game the players take turns being the acting player.  Each player's turn as the acting player consists of several different phases.
1. TurnInCards - After turns with a successful attack, players receive cards.  Once a set of cards has been obtained, it can be turned in for bonus troops at the beginning of a turn.  If a player has 5 or more cards, they must turn in cards, otherwise, they can pass.  
2. Place - players receive an allotment of troops at the beginning of each turn, based on their current holdings. Each Place action will place a single troop on the selected territory, that must be owned by the acting player. 
3. Attack - once all troops are placed the player can attack.  Each attack consists of an attacking territory (owned by the acting player), and an adjacent defending territory (owned by someone else).  An attack consists of a single roll of k dice for the attacker, where k can be at most 3, and no more than the number of troops in the attacking territory minus one.  The defender can roll 1 die if there is only one troop on the defending territory, and 2 dice otherwise. After each dice roll, the attacker and defender dice are sorted and then paired up, highest to highest, next-highest to next-highest.  Whichever player has the higher die in each case wins that battle, and the other player loses a troop from their territory, with ties being a win for the defender.  A player can stop attacking at any time and move to the Fortify phase. 
4. Occupy - After a successful attack, the acting player gets to decide how many troops to place in the conquered territory.  This can be at most n-1, if there are n troops in the attacking territory (one must be left behind), and at least k (the number of dice that were rolled). After occupation, the attacker can attack more territories. 
5. Fortify - In this phase, the player can move any number of troops from one territory to an adjacent one, as long as both are owned by the acting player.  At least 1 troop must be left on the source territory. 

Once a player has finished the fortify action, the next player has their turn. 
If a player occupies the last territory owned by another player, the attacking player gets all of the conquered player's cards, and the conquered player is out of the game.  The new cards might necessitate a return to the TurnInCards phase of the game, followed by Place and then back to attacking. 

As soon as one player occupies all territories on the map, they are the winner!

************************
Interactive RISK Program
************************

risk.pyw

This game is relatively simple to play.  There are a few phases in the game.
1.  In pregame you create players.  

To create players, go to the Player menu and choose "New Player." You can type in a name, or, alternatively, click on "Set AI" and find the AI program you wish to use. Click ok when you're done with that.

Once you've created enough players, you can choose to start the game by clicking on "Start Game" under the player menu

The rest of the game proceeds by clicking on territories for placement, attacking, and fortification.


******************************
To play a match between agents
******************************

play_risk_ai.py

This will play a game between specified AIS. It can save the resulting logfiles out to the matches folder, with the logfile name including participating agent names and the time of the match.

usage: play_risk_ai.py [-h] [-n, --num NUM] [-w, --write] [-v, --verbose]
                       ais [ais ...]

Play a RISK match between some AIs

positional arguments:
  ais            List of the AIs for match: ai_1 name_1 ai_2 name_2 . . .

optional arguments:
  -h, --help     show this help message and exit
  -n, --num NUM  Specify the number of games each player goes first in match
  -w, --write    Indicate that logfiles should be saved to the matches
                 directory
  -v, --verbose  Indicate that the match should be run in verbose mode

This gives each player 10 minutes per match, and limits the match to 5000 actions.  The player that goes first will alternate each game.

**************************
To view logs of AI matches
**************************

risk_game_viewer

This will allow you to visually follow a match logfile.  

Usage: python risk_game_viewer.py LOGFILE.log

You can click next to step through the actions and states, or hit play to have it do it automatically.  The player and action information are displayed on the left of the screen. 

*********************
To create your own AI
*********************

Start with a copy of random_ai.py or attacker_ai.py and fill out the agent with your code.  Look at the risktools.m.html file for an overview of the code.  You can specify how to choose an action in each case. 

**************************
Related RISK AI Resources
**************************
Some sources that could prove helpful: 

http://cs229.stanford.edu/proj2012/LozanoBratz-ARiskyProposalDesigningARiskGamePlayingAgent.pdf
  This is a student project in Stanford's ML class: uses Monte Carlo simulation and heuristic search

http://www.ke.tu-darmstadt.de/lehre/arbeiten/diplom/2005/Wolf_Michael.pdf
  A PhD thesis that uses reinforcement learning

https://martinsonesson.wordpress.com/2018/01/07/creating-an-ai-for-risk-board-game/
  A discussion of how to make AI players for Risk

http://richardggibson.appspot.com/static/work/10aiide-risk/10aiide-risk-paper.pdf
  A paper on a technique for selecting territories at the beginning of RISK

