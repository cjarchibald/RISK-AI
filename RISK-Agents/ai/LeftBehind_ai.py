"""
Team Left Behind.
"""

import riskengine
import riskgui
import random
from aihelper import *
from turbohelper import *
from risktools import *
from array import array

#This is the function implement to implement an AI.  Then this ai will work with either the gui or the play_risk_ai script
def getAction(state, time_left=None):
    """This is the main AI function.  It should return a valid AI action for this state."""
    
    #Get the possible actions in this state
    actions = getAllowedActions(state)
        
    #Select a Random Action
    myaction = random.choice(actions)
    
    #Get the PreAssign or Preplace Action
    if state.turn_type == 'PreAssign' or state.turn_type == 'PrePlace':
        myaction = pickCountry(state, actions)
        
    #Get the Attack or Fortify Action
    if state.turn_type == 'Attack' or state.turn_type == 'Fortify':
        myaction = forwardCountry(state, actions)
    
    #Get the Place Action
    if state.turn_type == 'Place':
        myaction = placeCountry(state,actions)
    
    return myaction

#This function selects the best PreAssign or Preplace Action
def pickCountry(state, actions):    
    possible_countries = []
    
    #Countries we want to conquer
    first_countries = ['Indonesia', 'New Guinea', 'Western Australia', 'Eastern Australia']                 #Countries wanted to conquer first(Australia)
    second_countries = ['Brazil', 'Peru', 'Colombia', 'Chile']                                              #Countries wanted to conquer second(Brazil)
    third_countries = ['Alaska','Mexico','Japan','Laos','Western Africa', 'Madagascar', 'Sweden','Iceland'] #Countries to keep opponent from gaining whole continent
    
    die = random.randint(1,3)           #Pick a random number between 1 and 3
    
    #Find all countries that we can conquer
    for a in actions:
        if a.to_territory is not None:
            possible_countries.append(a.to_territory)
            
    #Decide which countries to conquer
    # if die is 1, see if any of the first countries(Austrailia) are available and return action
    # else if die is 2, see if any of the second countries(South America) are available and return action
    # else if any of the third countries are available then conquer or just return the last action seen
    if die == 1:
        for i in first_countries:
            if i in possible_countries:
                return actions[possible_countries.index(i)]
    elif die == 2:
        for i in second_countries:
            if i in possible_countries:
                return actions[possible_countries.index(i)]
    for i in third_countries:
        if i in possible_countries:
            return actions[possible_countries.index(i)]
    return a
    
#Attack and Fortify Strategy
def forwardCountry(state, actions):
    possible_borders = []
    all_actions = []
    
    #Find all actions that can be taken
    for a in actions:
        if a.to_territory is not None:
            for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        possible_borders.append(a.to_territory)
            all_actions.append(a.to_territory)                      #Hold is name of all actions
    
    # This will count the number of occurences that a country appears in the possible borders
    country_counter = {}
    for country in possible_borders:
        if country in country_counter:
            country_counter[country] +=1
        else:
            country_counter[country] = 1
    countries = sorted(country_counter, country_counter.get, reverse = True)        #sort the list
    
    country = countries[:1]                                                         #stores the country that occurs the most(most surrounded country)
    
    #Find all of the indices for the most surrounded country
    #Check for the number of armies of our territories and return the action that will have most success
    if len(country)> 0:
        indices =[i for i, x in enumerate(all_actions) if x == country[0]]
        for x in indices:
            armies = 0
            if armies < state.armies[state.board.territory_to_id[actions[x].from_territory]]:
                armies = state.armies[state.board.territory_to_id[actions[x].from_territory]]
                index = x;
        return actions[index]

    return actions[0]

#Strategy used for the Place Action
def placeCountry(state,actions):  
    possible_borders = []
    all_actions = []

    #Find all possible borders
    for a in actions:
        if a.to_territory is not None:
            for n in state.board.territories[state.board.territory_to_id[a.to_territory]].neighbors:
                    if state.owners[n] != state.current_player:
                        possible_borders.append(a.to_territory)
            all_actions.append(a.to_territory)                      #Store all action names
    
    #Find the country that appears the most in possible borders
    country_counter = {}
    for country in possible_borders:
        if country in country_counter:
            country_counter[country] +=1
        else:
            country_counter[country] = 1
    countries = sorted(country_counter, country_counter.get, reverse = True)
    
    country = countries[:1]

    #Return the action of our country that is bordering that country to place armies there.
    if len(country) > 0:
       if country[0] in all_actions:
            return actions[all_actions.index(country[0])]

    return actions[0]  
    
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

  