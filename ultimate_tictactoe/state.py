import numpy as np
from mctspy.games.common import TwoPlayersAbstractGameState, AbstractGameAction


class UltimateTicTacToeMove(AbstractGameAction):
    def __init__(self, pos, value):
        self.pos = tuple(pos)
        self.value = value

    def __repr__(self):
        return "{0}: {1}".format(self.pos, self.value)


class UltimateTicTacToeGameState(TwoPlayersAbstractGameState):
    x = 1
    o = -1

    def __init__(self, board, last_move=None, next_to_move=1):
        if len(board.shape) != 4 or any(np.array(board.shape) != board.shape[0]):
            raise ValueError("Only 4D square boards allowed")
        self.last_move = last_move
        self.board = board
        self.board_size = board.shape[0]
        self.next_to_move = next_to_move

    def main_board(self):
        xsum = np.sum(self.board, 3)
        ysum = np.sum(self.board, 2)
        tl = self.board.trace(axis1=2, axis2=3)
        tr = self.board[::, ::, ::, ::-1].trace()

        n = self.board_size
        # zip the sums, each vector-couple represents a board
        xysum = np.stack((xsum, ysum), axis=2)
        # win = np.zeros((2,n,n), bool)
        win = [None, None]
        mainboard = np.zeros((n, n), int)
        for i, player in enumerate((-1, 1)):
            win[i] = np.any(xysum == player * n, axis=(2, 3))
            win[i] += tl == player * n
            win[i] += tr == player * n
            mainboard += player * win[i].astype(int)
        return mainboard

    @property
    def game_result(self):
        # check if game is over
        mainboard = self.main_board()
        rowsum = np.sum(mainboard, 0)
        colsum = np.sum(mainboard, 1)
        diag_sum_tl = mainboard.trace()
        diag_sum_tr = mainboard[::-1].trace()
        n = self.board_size
        winner = [False, False]
        for i, player in enumerate([-1, 1]):
            winner[i] |= any(rowsum == player * n)
            winner[i] |= any(colsum == player * n)
            winner[i] |= diag_sum_tl == player * n
            winner[i] |= diag_sum_tr == player * n
            if winner[i]:
                return player

        not_won_yet = self.board[mainboard.nonzero()]
        if np.all(not_won_yet != 0):
            return 0

        # if not over - no result
        return None

    def is_game_over(self):
        return self.game_result is not None

    def is_move_legal(self, move):
        # check if correct player moves
        if move.value != self.next_to_move:
            return False
        pos_in_range = min(move.pos) >= 0 and max(move.pos) <= self.board_size
        if not pos_in_range:
            return False
        # finally check if board field not occupied yet
        return self.board[move.pos] == 0

    def move(self, move):
        if not self.is_move_legal(move):
            raise ValueError(
                "move {0} on board {1} is not legal".format(move, self.board)
            )
        new_board = np.copy(self.board)
        new_board[move.pos] = move.value
        if self.next_to_move == UltimateTicTacToeGameState.x:
            next_to_move = UltimateTicTacToeGameState.o
        else:
            next_to_move = UltimateTicTacToeGameState.x

        return UltimateTicTacToeGameState(new_board, move, next_to_move)

    def get_legal_actions(self):
        player = self.next_to_move
        last = self.last_move and self.last_move.pos[2:]  # next row, col
        mainboard = self.main_board()
        ignore_last = not last or mainboard[last] != 0 or np.all(self.board[last] != 0)
        n = self.board_size
        moves = []
        for r in range(n):
            for c in range(n):
                if mainboard[r, c] == 0 and ((r, c) == last or ignore_last):
                    nonz_coord = np.argwhere(self.board[r, c] == 0)
                    moves += [UltimateTicTacToeMove((r, c, *pos), self.next_to_move) for pos in nonz_coord]
        return moves
