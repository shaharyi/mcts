import numpy as np

from mctspy.tree.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from mctspy.tree.search import MonteCarloTreeSearch
from mctspy.games.examples.tictactoe import TicTacToeGameState, TicTacToeMove

board = np.zeros((3,3))
initial_board_state = TicTacToeGameState(state=board, next_to_move=1)
state = initial_board_state

# root = TwoPlayersGameMonteCarloTreeSearchNode(state = state)
# mcts = MonteCarloTreeSearch(root)

while not state.is_game_over():
    if state.next_to_move == 1:
        root = TwoPlayersGameMonteCarloTreeSearchNode(state=state)
        mcts = MonteCarloTreeSearch(root)
        best_node = mcts.best_action(1000)
        action = best_node.action
    else:
        m = input("move:")
        m = int(m) - 1
        r = m // 3
        c = m % 3
        action = TicTacToeMove(r, c, -1)
    state = state.move(action)
    print(state.board)
