from common.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from common.search import MonteCarloTreeSearch
from ultimate_tictactoe.state import *

board = np.zeros((3, 3, 3, 3), int)
state = UltimateTicTacToeGameState(board, next_to_move=1)

# root = TwoPlayersGameMonteCarloTreeSearchNode(state = state)
# mcts = MonteCarloTreeSearch(root)

while not state.is_game_over():
    if state.next_to_move == 1:
        root = TwoPlayersGameMonteCarloTreeSearchNode(state=state)
        mcts = MonteCarloTreeSearch(root)
        best_node = mcts.best_action(100)
        action = best_node.action
    else:
        m = input("move:")
        board = int(m[0]) - 1
        c = int(m[1]) - 1
        pos = (board // 3, board % 3, c // 3, c % 3)
        action = UltimateTicTacToeMove(pos, -1)
    state = state.move(action)
    print(state.board)

print(('X wins!', 'Draw!', 'O wins!')[state.game_result + 1])
