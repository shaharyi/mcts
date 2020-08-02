from pdb import set_trace
import numpy as np

from flaskr.ultimate_tictactoe_form import UltimateTictactoeForm
from common.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from common.search import MonteCarloTreeSearch
from common.common import save_in_thread, load_object
from ultimate_tictactoe.state import UltimateTicTacToeMove, UltimateTicTacToeGameState

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from . import limiter    # flask limiter. Limits request rate

N = 3
NUM_ROLLOUTS = 100
TREE_FILENAME = 'ut_tree'
TREE_WEB_FILEPATH = '../../static/data/' + TREE_FILENAME
TREE_LOCAL_FILEPATH = 'flaskr/static/data/' + TREE_FILENAME

current_nodes = {}
session_id = 1
root = None

bp = Blueprint('ultimate_tictactoe', __name__, url_prefix='/ultimate_tictactoe')


def pos(i):
    b = i // (N * N)
    r, c = b // N, b % N
    p = i % (N * N)
    x, y = p // N, p % N
    return r, c, x, y


@bp.route('/ultimate_tictactoe/tree_view', methods=['GET'])
def tree_view():
    return render_template('tree_view.html', filepath='../../' + TREE_WEB_FILEPATH + '.d3.json')


@limiter.limit('10/minute; 60/hour; 100/day; 1000/month')
@bp.route('/ultimate_tictactoe', methods=['GET'])
def game_restart():
    global N, current_nodes, session_id, root
    root = load_object(TREE_LOCAL_FILEPATH)
    if not root:
        board = np.zeros((N, N, N, N), int)
        state = UltimateTicTacToeGameState(board=board, next_to_move=1)
        root = TwoPlayersGameMonteCarloTreeSearchNode(state=state)
    current_node = root
    state = current_node.state

    old_id = session.pop('id', None)  # in case a current game exists for this user
    if old_id:
        current_nodes.pop(old_id, None)
    session['id'] = session_id
    current_nodes[session_id] = current_node
    session_id += 1
    form = UltimateTictactoeForm()
    legal_moves = state.get_legal_actions(as_coords=True)
    mainboard = state.main_board()
    game_over, desig_board = None, None
    return render_template('ultimate_tictactoe.html', form=form, N=N,
                           game_over=game_over, board=state.board,
                           desig_board=desig_board, last_move=state.last_move,
                           legal_moves=legal_moves, mainboard=mainboard)


@limiter.limit('60/minute; 3000/hour; 8000/day; 40000/month')
@bp.route('/ultimate_tictactoe', methods=['GET'])
@bp.route('/ultimate_tictactoe', methods=['POST'])
def game():
    global N, current_nodes, root
    current_node = current_nodes.get(session['id'])
    if current_node is None:
        return redirect(url_for('hello'))
    state = current_node.state
    form = UltimateTictactoeForm()
    if form.validate_on_submit():
        print(state.main_board())
        if not state.is_game_over() and state.next_to_move == 1:
            m = request.form['pressed']
            m = int(m)
            action = UltimateTicTacToeMove(pos(m), 1)
            current_node = current_node.get_child(action)
            state = current_node.state
            if not state.is_game_over():
                mcts = MonteCarloTreeSearch(current_node)
                current_node = mcts.best_action(NUM_ROLLOUTS)
                state = current_node.state

    game_over = state.is_game_over()
    current_nodes[session['id']] = current_node
    mainboard = state.main_board()
    print('session_id=%d' % session['id'])
    print(mainboard)
    if game_over:
        flash(('O wins!', 'Draw!', 'X wins!')[state.game_result + 1])
        save_in_thread(TREE_LOCAL_FILEPATH, root)
        current_nodes.pop(session['id'])
        legal_moves = []
        desig_board = None
    else:
        legal_moves = state.get_legal_actions(as_coords=True)
        desig_board = state.last_move and state.last_move.pos[2:] or None
        if desig_board and mainboard[desig_board] != 0:
            desig_board = None
    return render_template('ultimate_tictactoe.html', form=form, N=N,
                           game_over=game_over, board=state.board,
                           desig_board=desig_board, last_move=state.last_move,
                           legal_moves=legal_moves, mainboard=mainboard)
