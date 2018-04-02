# RISK-AI
## Files
### risk.pyw

This game is relatively simple to play. Double click to run it. There are a few phases in the game.
1.  In pregame you create players.

To create players, go to the Player menu and choose "New Player." You can type in a name, or, alternatively, click on "Set AI" and find the AI program you wish to use. Click ok when you're done with that.

2.  Once you've created enough players, you can choose to start the game by clicking on "Start Game" under the player menu

3.  The rest of the game proceeds by clicking on territories for placement, attacking, and fortification.

### play_risk_ai.py

This will play a game between specified AIS. It saves the resulting logfile out to the matches folder, with the logfile name including participating agent names and the time of the match.

Usage: python play_risk_ai.py AI_1_File.py AI_1_Name AI_2_File.py AI_2_Name number_of_games

This gives each player 10 minutes per match, and limits the match to 5000 actions.  The player that goes first will alternate each game.

Note that *_bot.py ais will not function in this program.  They are only usable in risk.pyw.

### risk_game_viewer

This will allow you to visually follow a match logfile.

Usage: python risk_game_viewer.py LOGFILE.log

You can click next to step through the actions and states, or hit play to have it do it automatically.  The player and action information are displayed on the left of the screen.