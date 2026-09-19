from common.nodes import TwoPlayersGameMonteCarloTreeSearchNode, MonteCarloRaveNode
from common.search import MonteCarloTreeSearch
from ultimate_tictactoe.state import *
import numpy as np

USE_RAVE = False  # Toggle this True/False
NUM_ROLLOUTS = 100 if USE_RAVE else 2000

board = np.zeros((3, 3, 3, 3), int)
state = UltimateTicTacToeGameState(board, next_to_move=1)

# 1. Initialize the root OUTSIDE the loop so the tree is preserved!
if USE_RAVE:
    root_node = MonteCarloRaveNode(state=state)
else:
    root_node = TwoPlayersGameMonteCarloTreeSearchNode(state=state)

while not state.is_game_over():
    if state.next_to_move == 1:
        # Search using the preserved tree
        mcts = MonteCarloTreeSearch(root_node)
        best_node = mcts.best_action(NUM_ROLLOUTS)
        action = best_node.action
    else:
        m = input("move (e.g., 11): ")
        board_idx = int(m[0]) - 1
        c = int(m[1]) - 1
        pos = (board_idx // 3, board_idx % 3, c // 3, c % 3)
        action = UltimateTicTacToeMove(pos, -1)

    # Advance the game state
    state = state.move(action)

    # 2. Advance the tree down to the played move to keep its memory
    root_node = root_node.get_child(action)

    # Safety fallback just in case something goes wrong with action matching
    if root_node is None:
        if USE_RAVE:
            root_node = MonteCarloRaveNode(state=state)
        else:
            root_node = TwoPlayersGameMonteCarloTreeSearchNode(state=state)

    print(state.board)

print(('X wins!', 'Draw!', 'O wins!')[state.game_result + 1])
