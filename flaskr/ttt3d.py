from pdb import set_trace
import numpy as np

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from . import limiter  # flask limiter. Limits request rate

bp = Blueprint('ttt3d', __name__, url_prefix='/ttt3d')


@limiter.limit('10/minute; 60/hour; 100/day; 1000/month')
@bp.route('/ttt3d', methods=['GET'])
def game_restart():
    # Create a 4x4x4 board (Z, Y, X) -> (layer, row, col)
    # 0 = empty, 1 = X, -1 = O
    board = np.zeros((4, 4, 4), dtype=int)
    
    # Mock a 4x4x4 diagonal win for X (corner to opposite corner through the center)
    board[0][0][0] = 2   # Layer 0 (Top), top-left
    board[1][1][1] = 2   # Layer 1, mid-left
    board[2][2][2] = 2   # Layer 2, mid-right
    board[3][3][3] = 2   # Layer 3 (Bottom), bottom-right
    
    # Mock some random moves for O
    board[0][3][0] = -1  
    board[1][0][3] = -1  
    board[3][1][2] = -1  
    
    return render_template('ttt3d.html', board=board.tolist())

