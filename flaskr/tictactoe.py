from pdb import set_trace
import os.path
import numpy as np

from flaskr.tictactoe_form import TictactoeForm
from common.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from common.search import MonteCarloTreeSearch
from common.common import save_object_binary, load_object_binary
from tictactoe.tictactoe import TicTacToeGameState, TicTacToeMove

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('tictactoe', __name__, url_prefix='/tictactoe')
N = 3
state = None
root = None
current_node = None
TREE_FILENAME = 'ttt_tree'
WORKING_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(WORKING_DIR, 'static/data')
TREE_ABS_FILEPATH = os.path.join(DATA_DIR, TREE_FILENAME)
TREE_REL_FILEPATH = '../../static/data/' + TREE_FILENAME


@bp.route('/tictactoe/tree_view', methods=['GET'])
def tree_view():
    return render_template('tree_view.html', filepath=TREE_REL_FILEPATH + '.d3.json')


@bp.route('/tictactoe', methods=['GET'])
def game_restart():
    global state, N, root, current_node
    root = load_object_binary(TREE_ABS_FILEPATH)
    if root:
        state = root.state
    else:
        board = np.zeros((N, N), int)
        state = TicTacToeGameState(state=board, next_to_move=-1)
        root = TwoPlayersGameMonteCarloTreeSearchNode(state=state)
    current_node = root
    form = TictactoeForm()
    for i in range(N ** 2):
        form.buttons.entries[i].label.text = 'X O'[state.board[i // 3, i % 3] + 1]
    return render_template('tictactoe.html', form=form, N=N)


@bp.route('/tictactoe', methods=['POST'])
def game():
    global N, root, state, current_node
    form = TictactoeForm()
    if form.validate_on_submit():
        if not state.is_game_over() and state.next_to_move == -1:
            m = request.form['pressed']
            m = int(m) - 1
            r = m // 3
            c = m % 3
            action = TicTacToeMove(r, c, -1)
            current_node = current_node.get_child(action)
            state = current_node.state
            if not state.is_game_over():
                mcts = MonteCarloTreeSearch(current_node)
                best_node = mcts.best_action(1000)
                state = best_node.state
                current_node = best_node

    game_over = False
    if state.is_game_over():
        flash(('X wins!', 'Draw!', 'O wins!')[state.game_result + 1])
        game_over = True
        save_object_binary(TREE_ABS_FILEPATH, root)

    for i in range(N ** 2):
        form.buttons.entries[i].label.text = 'X O'[state.board[i // 3, i % 3] + 1]
    return render_template('tictactoe.html', form=form, N=N, game_over=game_over)
