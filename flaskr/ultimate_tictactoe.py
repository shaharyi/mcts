from pdb import set_trace
import numpy as np

from flaskr.ultimate_tictactoe_form import UltimateTictactoeForm
from mctspy.tree.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from mctspy.tree.search import MonteCarloTreeSearch
from ultimate_tictactoe.state import UltimateTicTacToeMove, UltimateTicTacToeGameState

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

N = 3
NUM_ROLLOUTS = 100

bp = Blueprint('ultimate_tictactoe', __name__, url_prefix='/ultimate_tictactoe')
state = None


def pos(i):
    b = i // (N * N)
    r, c = b // N, b % N
    p = i % (N * N)
    x, y = p // N, p % N
    return r, c, x, y


@bp.route('/ultimate_tictactoe', methods=['GET'])
def game_restart():
    global state, N
    board = np.zeros((N, N, N, N), int)
    state = UltimateTicTacToeGameState(board=board, next_to_move=-1)
    form = UltimateTictactoeForm()
    legal_moves = state.get_legal_actions(as_coords=True)
    mainboard = state.main_board()
    return render_template('ultimate_tictactoe.html', form=form, N=N,
                           game_over=False, board=state.board, legal_moves=legal_moves, mainboard=mainboard)


@bp.route('/ultimate_tictactoe', methods=['POST'])
def game():
    global state, N
    form = UltimateTictactoeForm()
    if form.validate_on_submit():
        if not state.is_game_over() and state.next_to_move == -1:
            m = request.form['pressed']
            m = int(m)
            action = UltimateTicTacToeMove(pos(m), -1)
            state = state.move(action)
            if not state.is_game_over():
                root = TwoPlayersGameMonteCarloTreeSearchNode(state=state)
                mcts = MonteCarloTreeSearch(root)
                best_node = mcts.best_action(NUM_ROLLOUTS)
                action = best_node.action
                state = state.move(action)

    game_over = False
    if state.is_game_over():
        flash(('X wins!', 'Draw!', 'O wins!')[state.game_result + 1])
        game_over = True

    legal_moves = state.get_legal_actions(as_coords=True)
    return render_template('ultimate_tictactoe.html', form=form, N=N,
                           game_over=game_over, board=state.board, legal_moves=legal_moves)
