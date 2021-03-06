from pdb import set_trace
import os.path
import numpy as np

from flaskr.tictactoe_form import TictactoeForm
from common.nodes import MonteCarloRaveNode
from common.search import MonteCarloTreeSearch
from common.common import load_object_binary, save_object_binary, save_object_text
from tictactoe.tictactoe import TicTacToeGameState, TicTacToeMove

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from . import limiter  # flask limiter. Limits request rate

bp = Blueprint('tictactoe', __name__, url_prefix='/tictactoe')

N = 3
TREE_FILENAME = 'ttt_tree'
WORKING_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(WORKING_DIR, 'static/data')
TREE_ABS_FILEPATH = os.path.join(DATA_DIR, TREE_FILENAME)
TREE_REL_FILEPATH = '../../static/data/' + TREE_FILENAME

# Global variables work well in deployment only if you set in apache single process.
# Otherwise they reset sometimes.
# /etc/apache2/sites-enabled/000-default.conf
# WSGIDaemonProcess mcts processes=1 threads=16
current_nodes = {}
session_id = 1
root = None


@limiter.limit('10/minute; 60/hour; 100/day; 1000/month')
@bp.route('/tictactoe/tree_view', methods=['GET'])
def tree_view():
    return render_template('tree_view.html', filepath=TREE_REL_FILEPATH + '.d3.json')


@limiter.limit('10/minute; 60/hour; 100/day; 1000/month')
@bp.route('/tictactoe', methods=['GET'])
def game_restart():
    global N, current_nodes, session_id, root
    root = load_object_binary(TREE_ABS_FILEPATH)
    if root:
        state = root.state
    else:
        board = np.zeros((N, N), int)
        state = TicTacToeGameState(board=board, next_to_move=-1)
        root = MonteCarloRaveNode(state=state)
    current_node = root
    state = current_node.state

    old_id = session.pop('id', None)  # in case a current game exists for this user
    if old_id:
        current_nodes.pop(old_id, None)
    session['id'] = session_id
    current_nodes[session_id] = current_node
    session_id += 1

    form = TictactoeForm()
    for i in range(N ** 2):
        form.buttons.entries[i].label.text = 'X O'[state.board[i // 3, i % 3] + 1]
    return render_template('tictactoe.html', form=form, N=N)


@limiter.limit('120/minute; 3000/hour; 8000/day; 40000/month')
@bp.route('/tictactoe', methods=['POST'])
def game():
    global N, current_nodes, root
    current_node = current_nodes.get(session['id'])
    if current_node is None:
        flash('Bug caused reset!    Sorry for that.')
        return redirect(url_for('hello'))
    state = current_node.state
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

    current_nodes[session['id']] = current_node
    game_over = False

    if state.is_game_over():
        flash(('X wins!', 'Draw!', 'O wins!')[state.game_result + 1])
        game_over = True
        save_object_binary(TREE_ABS_FILEPATH, root)
        save_object_text(TREE_ABS_FILEPATH, root)
        current_nodes.pop(session['id'])

    for i in range(N ** 2):
        form.buttons.entries[i].label.text = 'X O'[state.board[i // 3, i % 3] + 1]
    return render_template('tictactoe.html', form=form, N=N, game_over=game_over)
