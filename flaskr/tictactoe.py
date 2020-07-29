from pdb import set_trace
import numpy as np

from flaskr.tictactoe_form import TictactoeForm
from mctspy.tree.nodes import TwoPlayersGameMonteCarloTreeSearchNode
from mctspy.tree.search import MonteCarloTreeSearch
from mctspy.games.examples.tictactoe import TicTacToeGameState, TicTacToeMove

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('tictactoe', __name__, url_prefix='/tictactoe')
N = 3
state = None


@bp.route('/tictactoe', methods=['GET'])
def game_restart():
    global state, N
    board = np.zeros((N, N), int)
    state = TicTacToeGameState(state=board, next_to_move=-1)
    form = TictactoeForm()
    for i in range(N ** 2):
        form.buttons.entries[i].label.text = 'x-o'[state.board[i // 3, i % 3] + 1]
    return render_template('tictactoe.html', form=form, N=N)


@bp.route('/tictactoe', methods=['POST'])
def game():
    global state, N
    form = TictactoeForm()
    if form.validate_on_submit():
        if not state.is_game_over() and state.next_to_move == -1:
            m = request.form['pressed']
            m = int(m) - 1
            r = m // 3
            c = m % 3
            action = TicTacToeMove(r, c, -1)
            state = state.move(action)
            if not state.is_game_over():
                root = TwoPlayersGameMonteCarloTreeSearchNode(state=state)
                mcts = MonteCarloTreeSearch(root)
                best_node = mcts.best_action(1000)
                action = best_node.action
                state = state.move(action)

    game_over = False
    if state.is_game_over():
        flash(('X wins!', 'Draw!', 'O wins!')[state.game_result + 1])
        game_over = True

    for i in range(N ** 2):
        form.buttons.entries[i].label.text = 'x-o'[state.board[i // 3, i % 3] + 1]
    return render_template('tictactoe.html', form=form, N=N, game_over=game_over)
