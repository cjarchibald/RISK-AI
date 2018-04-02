import random
from gui.aihelper import *
from gui.turbohelper import *
from risktools import *

# It's like the Ottoman Empire, but with Armchairs instead

# Eric Timms, Cooper Anderton, Christian Shelby

# For determining territories
northAm = ("Alaska","NorthwestTerritories","Greenland","British Columbia","Ontario","Quebec","Western U.S.","Eastern U.S.","Mexico")
southAm = ("Colombia","Brazil","Peru","Chile")
africa = ("South Africa","Zaire","Etiopia","Middle East","Egypt","Western Africa","Madagascar")

fortifyFlag = 0

def getAction(state, time_left=None):
	"""This is the main AI function.  It should return a valid AI action for this state."""
    
	#Get the possible actions in this state
	actions = getAllowedActions(state)

	#Random initial choice
	myaction = random.choice(actions)

## -----------------------------------------
## Beginning of Game
## -----------------------------------------
	if state.turn_type == 'PreAssign':

		# Our main gameplan is to try to take and start from the Ameicas, as they have the fewest points of entry
		# Our first choice is to try and hold all of these "bridge" territories
		for a in actions:
			if(a.to_territory == "Brazil"):
				return a
			if(a.to_territory == "Alaska"):
				return a			
			if(a.to_territory == "Greenland"):
				return a
	
		# If Brazil, Alaska, and Greenland aren't available

		# First try to take any territory in North America
		for a in actions:
			if(a.to_territory in northAm):
				return a

		# Second, any territory in South America
		for a in actions:
			if(a.to_territory in southAm):
				return a

		# Third, any territory in Africa
		for a in actions:
			if(a.to_territory in africa):
				return a

		# Otherwise we will return our initial random 

	if state.turn_type == 'PrePlace':

		# First want to try to reinforce our ideal border territories
		for a in actions:
			
			if(a.to_territory == "Brazil" or "Alaska" or "Greenland"):

				aTerrId = state.board.territory_to_id[a.to_territory]

				# For every neighbor of these territories
				for n in state.board.territories[aTerrId].neighbors:

					# If we don't own it, that is another player is on those bordering territories
					if state.owners[n] != state.current_player:

						# If the armies of the neighbor +1 is greater than the armies of our territory
						if((state.armies[n] + 1) > state.armies[aTerrId]):

							# We want to make sure we have more players than them in these territories
							return a

		possible_actions = []

		# Otherwise, place troops anywhere near enemy territories
		for a in actions:
			if a.to_territory is not None:
				for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
					if state.owners[n] != state.current_player:
						possible_actions.append(a)
                    
		if len(possible_actions) > 0:
			myaction = random.choice(possible_actions)

		return myaction
		

## Normal Turns
				
	if state.turn_type == 'TurnInCards':

		## Turn in cards if we have the option
		myaction = random.choice(actions)
		return myaction

## Attacking

	if state.turn_type == 'Attack':
		myaction = random.choice(actions)	

		## Decide if we want to attack, or what actions are accpetable.

		possible_actions = []

		# To determine if we have a territory 'surrounded'
		surroundedFlag = 1

		# We're attempting to play somewhat defensively

		# Checking every action
		for a in actions:
			if a.to_territory is not None:

				# ID of the territory attacking
				attack = state.board.territory_to_id[a.from_territory]

				# ID of the territory defending
				defend = state.board.territory_to_id[a.to_territory]

				# Only plan on attacking if we have 2 more troops than the defending territory
				if (state.armies[defend] + 1) < state.armies[attack]:

					# Looking at all the neighbors of the defending territory
					for n in state.board.territories[defend].neighbors:

						# If someone else owns it, and they have less armies than our attacking state
						# This is an attempt to make it so when we Occupy it, we should be able to do so with more than the neighbors
						if state.owners[n] != state.current_player and state.armies[n] < state.armies[attack]:

							possible_actions.append(a)

							# If we don't own 1 of it's neighboring states, we don't have the territory surrounded
							sourroundedFlag = 0

					# If this flag is still up, we are surrounding this territory, and will immidiately attempt to take it
					if surroundedFlag == 1:
						return a

			# This action will end our attack phase
			if a.to_territory is None:
				endAttack = a
					
		# Choose a possible action
		if len(possible_actions) > 0:
			myaction = random.choice(possible_actions)

		# If we don't have anything in possible_actions, then none of our attack criteria have been fullfilled
		else:
			# So, we will end our Attack
			return endAttack


	if state.turn_type == 'Occupy':

		surroundedFlag = 1

		possible_actions = []
		
		# Checking every action
		for a in actions:

			# ID of the territory being occupied
			movingTo = state.board.territory_to_id[a.to_territory]
			movingFrom = state.board.territory_to_id[a.from_territory]

			for n in state.board.territories[movingTo].neighbors:

				if state.owners[n] != state.current_player and a.troops > 2:
					
					possible_actions.append(a)
					sourroundedFlag = 0

			# If we have a territory surrounded, we only want to move one troop there
			if surroundedFlag == 1 and a.troops == 1:
				return a

		if len(possible_actions) > 0:
			myaction = random.choice(possible_actions)
    
	if state.turn_type == 'Place' or state.turn_type == 'Fortify':
		possible_actions = []

		for a in actions:

			if a.to_territory is not None:
				for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
					if state.owners[n] != state.current_player:
						possible_actions.append(a)
                    
		if len(possible_actions) > 0:
			myaction = random.choice(possible_actions)
        
                    
	return myaction

#Stuff below this is just to interface with Risk.pyw GUI version
#DO NOT MODIFY
    
def aiWrapper(function_name, occupying=None):
    game_board = createRiskBoard()
    game_state = createRiskState(game_board, function_name, occupying)
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

