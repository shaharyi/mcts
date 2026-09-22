from dataclasses import dataclass
from dataclasses_json import dataclass_json
import numpy as np
from common.common import TwoPlayersAbstractGameState, AbstractGameAction


def generate_winning_lines():
    lines = []
    # 1D Axis Parallel Lines (48)
    for i in range(4):
        for j in range(4):
            lines.append([(i, j, k) for k in range(4)])
            lines.append([(i, k, j) for k in range(4)])
            lines.append([(k, i, j) for k in range(4)])

    # 2D Plane Diagonals (24)
    for i in range(4):
        lines.append([(i, k, k) for k in range(4)])
        lines.append([(i, k, 3 - k) for k in range(4)])
        lines.append([(k, i, k) for k in range(4)])
        lines.append([(k, i, 3 - k) for k in range(4)])
        lines.append([(k, k, i) for k in range(4)])
        lines.append([(k, 3 - k, i) for k in range(4)])

    # 3D Space Diagonals (4)
    lines.append([(k, k, k) for k in range(4)])
    lines.append([(k, k, 3 - k) for k in range(4)])
    lines.append([(k, 3 - k, k) for k in range(4)])
    lines.append([(k, 3 - k, 3 - k) for k in range(4)])

    return lines


WINNING_LINES = generate_winning_lines()


@dataclass_json
@dataclass
class TicTacToe3DMove(AbstractGameAction):
    z_coordinate: int
    r_coordinate: int
    c_coordinate: int
    value: int

    def __str__(self):
        return f'{self.z_coordinate}, {self.r_coordinate}, {self.c_coordinate}, {self.value}'


@dataclass_json
@dataclass
class TicTacToe3DGameState(TwoPlayersAbstractGameState):
    board: np.ndarray
    x = 1
    o = -1

    def __init__(self, board=None, next_to_move=1):
        if board is None:
            self.board = np.zeros((4, 4, 4), dtype=int)
        else:
            if len(board.shape) != 3 or board.shape != (4, 4, 4):
                raise ValueError("Only 4x4x4 3D boards allowed")
            self.board = board

        self.board_size = 4
        self.next_to_move = next_to_move

    @property
    def game_result(self):
        """Calculates the game result dynamically across all 76 winning lines."""
        for line in WINNING_LINES:
            vals = [self.board[z, r, c] for z, r, c in line]
            if len(set(vals)) == 1 and vals[0] != 0:
                return self.x if vals[0] > 0 else self.o

        if np.all(self.board != 0):
            return 0  # Draw

        return None

    def is_game_over(self):
        return self.game_result is not None

    def is_move_legal(self, move):
        if move.value != self.next_to_move:
            return False

        z_in_range = (0 <= move.z_coordinate < self.board_size)
        if not z_in_range:
            return False

        r_in_range = (0 <= move.r_coordinate < self.board_size)
        if not r_in_range:
            return False

        c_in_range = (0 <= move.c_coordinate < self.board_size)
        if not c_in_range:
            return False

        return self.board[move.z_coordinate, move.r_coordinate, move.c_coordinate] == 0

    def move(self, move):
        if not self.is_move_legal(move):
            raise ValueError(f"move {move} on board is not legal")

        new_board = np.copy(self.board)
        new_board[move.z_coordinate, move.r_coordinate, move.c_coordinate] = move.value

        if self.next_to_move == TicTacToe3DGameState.x:
            next_to_move = TicTacToe3DGameState.o
        else:
            next_to_move = TicTacToe3DGameState.x

        next_state = TicTacToe3DGameState(new_board, next_to_move)

        # Highlight winning tokens (2 for Red, -2 for Blue) if move ends the game
        res = next_state.game_result
        if res in (self.x, self.o):
            highlight = 2 if res == self.x else -2
            for line in WINNING_LINES:
                vals = [next_state.board[z, r, c] for z, r, c in line]
                if len(set(vals)) == 1 and vals[0] in (1, -1):
                    for wz, wr, wc in line:
                        next_state.board[wz, wr, wc] = highlight

        return next_state

    def get_legal_actions(self):
        if self.is_game_over():
            return []

        indices = np.where(self.board == 0)
        return [
            TicTacToe3DMove(coords[0], coords[1], coords[2], self.next_to_move)
            for coords in list(zip(indices[0], indices[1], indices[2]))
        ]

    def evaluate(self):
        """Scores position strength across all 76 winning lines for minimax.py."""
        score = 0
        for line in WINNING_LINES:
            vals = [self.board[z, r, c] for z, r, c in line]
            p1 = vals.count(1) + vals.count(2)
            p2 = vals.count(-1) + vals.count(-2)

            if p1 > 0 and p2 > 0:
                continue

            if p1 > 0:
                if p1 == 3: score += 150
                elif p1 == 2: score += 15
                elif p1 == 1: score += 1
            elif p2 > 0:
                if p2 == 3: score -= 150
                elif p2 == 2: score -= 15
                elif p2 == 1: score -= 1

        return score