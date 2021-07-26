import numpy as np

from common.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from common.search import MonteCarloTreeSearch
from tictactoe.tictactoe import TicTacToeGameState, TicTacToeMove

board = np.zeros((3, 3), int)
state = TicTacToeGameState(board, next_to_move=-1)

# root = TwoPlayersGameMonteCarloTreeSearchNode(state = state)
# mcts = MonteCarloTreeSearch(root)

while not state.is_game_over():
    if state.next_to_move == 1:
        root = TwoPlayersGameMonteCarloTreeSearchNode(state=state)
        mcts = MonteCarloTreeSearch(root)
        best_node = mcts.best_action(1000)
        action = best_node.action
    else:
        m = input("move 1..9: ")
        m = int(m) - 1
        r = m // 3
        c = m % 3
        action = TicTacToeMove(r, c, -1)
    state = state.move(action)
    print(state.board)

print(('X wins!', 'Draw!', 'O wins!')[state.game_result + 1])
