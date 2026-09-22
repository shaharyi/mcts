import numpy as np

from flaskr.ultimate_tictactoe_form import UltimateTictactoeForm
from ultimate_tictactoe.state import UltimateTicTacToeMove, UltimateTicTacToeGameState
from common.minimax import get_best_action_minimax

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from . import limiter

N = 3
MINIMAX_TIME_LIMIT = 3.0  # Seconds the bot is allowed to "think"

# We no longer need to save a giant MCTS tree to disk!
current_states = {}
session_id = 1

bp = Blueprint('ultimate_tictactoe', __name__, url_prefix='/ultimate_tictactoe')


def pos(i):
    b = i // (N * N)
    r, c = b // N, b % N
    p = i % (N * N)
    x, y = p // N, p % N
    return r, c, x, y


@limiter.limit('10/minute; 60/hour; 100/day; 1000/month')
@bp.route('/ultimate_tictactoe', methods=['GET'])
def game_restart():
    global N, current_states, session_id

    # Initialize a fresh state
    board = np.zeros((N, N, N, N), int)
    state = UltimateTicTacToeGameState(board=board, next_to_move=1)

    old_id = session.pop('id', None)
    if old_id:
        current_states.pop(old_id, None)

    session['id'] = session_id
    current_states[session_id] = state
    session_id += 1

    form = UltimateTictactoeForm()
    legal_moves = state.get_legal_actions(as_coords=True)
    mainboard = state.main_board()

    return render_template('ultimate_tictactoe.html', form=form, N=N,
                           game_over=None, board=state.board,
                           desig_board=None, last_move=state.last_move,
                           legal_moves=legal_moves, mainboard=mainboard)


@limiter.limit('120/minute; 3000/hour; 8000/day; 40000/month')
@bp.route('/ultimate_tictactoe', methods=['POST'])
def game():
    global N, current_states

    state = current_states.get(session['id'])
    if state is None:
        flash('Bug caused reset! Sorry for that.')
        return redirect(url_for('ultimate_tictactoe.game_restart'))

    form = UltimateTictactoeForm()

    if form.validate_on_submit():
        # If it's the human's turn
        if not state.is_game_over() and state.next_to_move == 1:
            m = int(request.form['pressed'])
            action = UltimateTicTacToeMove(pos(m), 1)
            state = state.move(action)

            # If the human move didn't end the game, trigger the Bot
            if not state.is_game_over():
                # --- THIS IS WHERE MINIMAX REPLACES MCTS ---
                bot_action = get_best_action_minimax(state, time_limit=MINIMAX_TIME_LIMIT)
                state = state.move(bot_action)
                # -------------------------------------------

    game_over = state.is_game_over()
    current_states[session['id']] = state
    mainboard = state.main_board()

    if game_over:
        flash(('O wins!', 'Draw!', 'X wins!')[state.game_result + 1])
        current_states.pop(session['id'])
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
