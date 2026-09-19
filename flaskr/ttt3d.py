from flask import Flask, render_template
import numpy as np

app = Flask(__name__)

@app.route('/')
def tictactoe_4x4x4():
    # Create a 4x4x4 board (Z, Y, X) -> (layer, row, col)
    # 0 = empty, 1 = X, -1 = O
    board = np.zeros((4, 4, 4), dtype=int)
    
    # Mock a 4x4x4 diagonal win for X (corner to opposite corner through the center)
    board[0][0][0] = 1   # Layer 0 (Top), top-left
    board[1][1][1] = 1   # Layer 1, mid-left
    board[2][2][2] = 1   # Layer 2, mid-right
    board[3][3][3] = 1   # Layer 3 (Bottom), bottom-right
    
    # Mock some random moves for O
    board[0][3][0] = -1  
    board[1][0][3] = -1  
    board[3][1][2] = -1  
    
    return render_template('ttt3d.html', board=board.tolist())

if __name__ == '__main__':
    app.run(debug=True)