"""This is the primary module for the Khan AI. It defines an Intelligence
class which peforms most of Khan's look-ahead and heuristic evaluation
behavior.

"""

import Queue
import random
import time

import heuristics as hr

from risktools import *

class Intelligence:
    """This class encapsulates intelligence look-ahead and heuristic evaluation
    behavior for the Khan AI.

    """

    general_hr_set = [hr.troop_standard_deviation,
                      hr.percent_continents_owned,
                      hr.percent_troops_wasted,
                      hr.easily_defended_continents,
                      hr.match_threatening_territories,
                      hr.threatened_borders]

    action_heuristics = {"PreAssign": general_hr_set,
                         "PrePlace": general_hr_set,
                         "Place": general_hr_set,
                         "TurnInCards": general_hr_set,
                         "Attack": general_hr_set,
                         "Occupy": general_hr_set,
                         "Fortify": general_hr_set,
                         "GameOver": []}

    def __init__(self, time_limit, action_limit, weights_path,
                 depth_limit=None):
        """Initialize an Intelligence instance.

        :param time_limit: Total time for game in seconds
        :type time_limit: float
        :param action_limit: Total number of actions for game
        :type action_limit: int
        :param weights_path: Name of file containing heuristics weights
        :type weights_path: str
        :param depth_limit: Maximum number of plys to search ahead in game,
                            defaults to None indicating no maximum
        :type depth_limit: int

        """

        # Assign equal time to all actions during game
        self.action_max_time = time_limit / action_limit

        self.depth_limit = depth_limit
        self.weights = []

        self.__load_weights(weights_path)

    def __load_weights(self, weights_path):
        """Load weights into weights list from a file.

        :param weights_path: Path to file containing weights
        :type weights_path: str

        """

        with open(weights_path, "r") as weights_file:
            for line in weights_file.readlines():
                self.weights.append(int(line))

    def __check_value(self, state):
        """Check the heuristic value of any state based on the turn type for
        the state.
  
        :param state: State of game
        :type state: RiskState

        :returns: Heuristic value for state
        :rtype: float

        """
        
        turn_type = state.turn_type
        
        state_value = 0

        # Total state value is sum of weight * heuristic per heuristic
        for index, heuristic in \
            enumerate(Intelligence.action_heuristics[turn_type]):
            state_value += self.weights[index] * heuristic(state)

        return state_value
    
    def get_action(self, state):
        """Return the best action to take based on the current state of
        the game.

        :param state: State of game
        :type state: RiskState

        :returns: Best action for Intelligence based on look-ahead
        :rtype: RiskAction

        """

        start_time = time.time()
        queue = Queue.PriorityQueue()

        # Put the current state in the queue
        # None represents that it takes no action to get here
        # and 0 shows that this state is at depth 0 to the start state
        queue.put([0, state, None, 0])

        # Continue looking ahead while time is available for this action
        while (time.time() - start_time) < self.action_max_time:
            current_value, current_state, init, depth  = queue.get()

            # Check that we haven't passed depth limit
            if self.depth_limit is not None:
                if depth > self.depth_limit:
                    # Put the action we pulled out back into the queue
                    queue.put([current_value, current_state, init, \
                               depth])
                    break

            # Get all possible actions to take from this state
            possible_actions = getAllowedActions(current_state)

            # If we're in a gameover state, there will be no possible actions
            if not possible_actions or len(possible_actions) == 0:
                continue

            for action in possible_actions:
                # Get the vector of possible successors and their probabilities
                successors, probabilities = simulateAction(current_state,
                                                                 action)

                # Roll over each successor state
                for successor, probability in zip(successors, probabilities):
                    # Final state value is computed heuristic value times
                    # likelihood of that state occuring
                    state_value = self.__check_value(successor) * probability

                    # We only really care about the immediate action (i.e. the
                    # action that leads to states one ply away, so we'll only
                    # keep track of that, and keep track of depth for all other
                    # actions
                    if depth == 0:
                        queue.put([-state_value,
                                   successor,
                                   action,
                                   depth + 1])
                    # Otherwise we don't want to change the initial action
                    else:
                        queue.put([-state_value,
                                   successor,
                                   init,
                                   depth + 1])

                    # State value is negative so the default Python min-priority
                    # queue becomes a max PQ
                    # from suggestion by Martijn Pieters at
                    # stackoverflow.com/questions/15124097

        # Unwrap the best action from the list in the queue
        value, successor_state, best_action, depth = queue.get()

        return best_action
