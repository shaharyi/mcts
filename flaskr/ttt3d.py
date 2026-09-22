from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flaskr.ultimate_tictactoe_form import UltimateTictactoeForm
from tictactoe_3d.ttt3d_state import TicTacToe3DGameState, TicTacToe3DMove
from common.minimax import get_best_action_minimax

bp = Blueprint('ttt3d', __name__, url_prefix='/ttt3d')

current_states = {}
session_id = 1


@bp.route('/ttt3d', methods=['GET'])
def game_restart():
    global session_id, current_states

    state = TicTacToe3DGameState()

    old_id = session.pop('ttt3d_id', None)
    if old_id:
        current_states.pop(old_id, None)

    session['ttt3d_id'] = session_id
    current_states[session_id] = state
    session_id += 1

    form = UltimateTictactoeForm()
    return render_template('ttt3d.html', form=form, board=state.board, game_over=False)


@bp.route('/ttt3d', methods=['POST'])
def game():
    global current_states

    state_id = session.get('ttt3d_id')
    state = current_states.get(state_id)

    if state is None:
        return redirect(url_for('ttt3d.game_restart'))

    form = UltimateTictactoeForm()

    if request.method == 'POST':
        try:
            z = int(request.form['pressed_z'])
            r = int(request.form['pressed_r'])
            c = int(request.form['pressed_c'])

            # Wrap in TicTacToe3DMove dataclass to match get_legal_actions()
            user_move = TicTacToe3DMove(z_coordinate=z, r_coordinate=r, c_coordinate=c, value=state.next_to_move)

            if user_move in state.get_legal_actions() and not state.is_game_over():
                # 1. Execute Human Move
                state = state.move(user_move)

                # 2. Execute AI Move if game continues
                if not state.is_game_over():
                    ai_move = get_best_action_minimax(state, time_limit=2.0)
                    if ai_move:
                        state = state.move(ai_move)

                current_states[state_id] = state

        except (KeyError, ValueError):
            pass

    game_over = state.is_game_over()
    if game_over:
        res = state.game_result
        if res in (1, 2):
            flash('Player (Red) Wins!')
        elif res in (-1, -2):
            flash('AI (Blue) Wins!')
        else:
            flash('Draw!')

    return render_template('ttt3d.html', form=form, board=state.board, game_over=game_over)