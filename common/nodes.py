from pdb import set_trace
import numpy as np
from collections import defaultdict
from abc import ABC, abstractmethod

RAVE_C_FACTOR = 1.4
RAVE_B_FACTOR = 1
REWARD = {0: 0.5, 1: 1, -1: 0}  # draw gives 0.5, win gives 1, loss gives 0


class MonteCarloTreeSearchNode(ABC):
    state: object
    parent: object
    children: list

    def __init__(self, state, parent=None):
        """
        Parameters
        ----------
        state : mctspy.games.common.TwoPlayersAbstractGameState
        parent : MonteCarloTreeSearchNode
        """
        self.state = state
        self.parent = parent
        self.children = []

    @property
    @abstractmethod
    def untried_actions(self):
        """

        Returns
        -------
        list of mctspy.games.common.AbstractGameAction

        """
        pass

    @property
    @abstractmethod
    def w(self):
        pass

    @property
    @abstractmethod
    def n(self):
        pass

    @abstractmethod
    def expand(self):
        pass

    @abstractmethod
    def is_terminal_node(self):
        pass

    @abstractmethod
    def rollout(self):
        pass

    @abstractmethod
    def backpropagate(self, reward):
        pass

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c_param=1.4):
        choices_weights = [
            (c.w / c.n) + c_param * np.sqrt((2 * np.log(self.n) / c.n))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]


class TwoPlayersGameMonteCarloTreeSearchNode(MonteCarloTreeSearchNode):
    action: object
    _number_of_visits: int
    _wins: float
    _untried_actions: list

    def __init__(self, state, parent=None, action=None):
        super().__init__(state, parent)
        self.action = action
        self._number_of_visits = 0
        self._untried_actions = None
        self._wins = 0.0

    @property
    def untried_actions(self):
        if self._untried_actions is None:
            self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions

    @property
    def n(self):
        return self._number_of_visits

    @property
    def w(self):
        return self._wins

    def expand(self):
        action = self.untried_actions.pop()
        next_state = self.state.move(action)
        # be prepared to instantiate of inherited class
        child_node = self.__class__(next_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

    def expand_action(self, action):
        self.untried_actions.remove(action)
        next_state = self.state.move(action)
        # be prepared to instantiate of inherited class
        child_node = self.__class__(next_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

    def get_child(self, action):
        if action in self.untried_actions:
            self.expand_action(action)
        for c in self.children:
            if action == c.action:
                return c
        return None

    def is_terminal_node(self):
        return self.state.is_game_over()

    def rollout(self):
        current_rollout_state = self.state
        while not current_rollout_state.is_game_over():
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state = current_rollout_state.move(action)
        return current_rollout_state.game_result

    def update_stats(self, result):
        self._number_of_visits += 1.0
        result_for_self = -1  # assume self lost and gets zero reward
        if self.parent:
            result_for_self = result * self.parent.state.next_to_move
        self._wins += REWARD[result_for_self]

    def backpropagate(self, result):
        self.update_stats(result)
        if self.parent:
            self.parent.backpropagate(result)


class MonteCarloRaveNode(TwoPlayersGameMonteCarloTreeSearchNode):
    _number_of_visits_rave: int
    _wins_rave: float

    def __init__(self, state, parent=None, action=None):
        super().__init__(state, parent, action)
        self._number_of_visits_rave = 0
        self._wins_rave = 0.0

    @property
    def w_rave(self):
        return self._wins_rave

    @property
    def n_rave(self):
        return self._number_of_visits_rave

    def best_child(self, c_param=RAVE_C_FACTOR):
        def calc_beta(c):
            return c.n_rave / (c.n + c.n_rave + 4 * RAVE_B_FACTOR ** 2 * c.n * c.n_rave)

        choices_weights = []
        for c in self.children:
            beta = calc_beta(c)
            if beta != 0:
                weight = (1 - beta) * (c.w / c.n) + beta * (c.w_rave / c.n_rave) + \
                         c_param * np.sqrt((2 * np.log(self.n) / c.n))
            else:
                weight = c.w / c.n + c_param * np.sqrt((2 * np.log(self.n) / c.n))
            choices_weights.append(weight)
        return self.children[np.argmax(choices_weights)]

    def rollout(self):
        actions = set()
        current_rollout_state = self.state
        while not current_rollout_state.is_game_over():
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            actions.add(action.data)
            current_rollout_state = current_rollout_state.move(action)
        return current_rollout_state.game_result, actions

    def backpropagate(self, rollout_output):
        result, rollout_actions = rollout_output
        self.update_stats(result)
        if self.parent:
            for c in self.parent.children:
                if c.action.data in rollout_actions:
                    result_for_c = result * self.state.next_to_move
                    c._wins_rave += REWARD[result_for_c]
                    c._number_of_visits_rave += 1
            self.parent.backpropagate(rollout_output)
