import time
import numpy as np


def evaluate_grid(grid):
    """Evaluates a single 3x3 grid (can be a micro-board or the main macro-board)"""
    score = 0
    lines = [
        grid[0, :], grid[1, :], grid[2, :],
        grid[:, 0], grid[:, 1], grid[:, 2],
        grid.diagonal(), np.fliplr(grid).diagonal()
    ]

    for line in lines:
        s = sum(line)
        if s == 3: return 100
        if s == -3: return -100

        zeros = np.count_nonzero(line == 0)
        if s == 2 and zeros == 1: score += 10
        if s == -2 and zeros == 1: score -= 10
        if s == 1 and zeros == 2: score += 1
        if s == -1 and zeros == 2: score -= 1

    return score


def static_evaluation(state):
    """Scores the board position dynamically based on game state type."""
    if state.is_game_over():
        res = state.game_result() if callable(getattr(state, 'game_result', None)) else state.game_result
        if res == 1:
            return 100000
        elif res == -1:
            return -100000
        else:
            return 0  # Draw

    # If the state defines its own evaluation function (e.g., 3D Tic-Tac-Toe)
    if hasattr(state, 'evaluate'):
        return state.evaluate()

    # Default evaluation for Ultimate Tic-Tac-Toe
    score = 0
    main = state.main_board()
    score += evaluate_grid(main) * 100

    for r in range(3):
        for c in range(3):
            if main[r, c] == 0:
                micro_score = evaluate_grid(state.board[r, c])
                if r == 1 and c == 1:
                    micro_score *= 1.5
                score += micro_score

    return score


def minimax_alpha_beta(state, depth, alpha, beta, maximizing_player, start_time, time_limit):
    """Recursive Alpha-Beta Pruning with a strict timeout."""
    if time.time() - start_time > time_limit:
        raise TimeoutError()

    if depth == 0 or state.is_game_over():
        return static_evaluation(state), None

    legal_actions = state.get_legal_actions()
    if not legal_actions:
        return static_evaluation(state), None

    best_action = None

    if maximizing_player:
        max_eval = -float('inf')
        for action in legal_actions:
            child_state = state.move(action)
            eval_val, _ = minimax_alpha_beta(child_state, depth - 1, alpha, beta, False, start_time, time_limit)

            if eval_val > max_eval:
                max_eval = eval_val
                best_action = action

            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval, best_action

    else:
        min_eval = float('inf')
        for action in legal_actions:
            child_state = state.move(action)
            eval_val, _ = minimax_alpha_beta(child_state, depth - 1, alpha, beta, True, start_time, time_limit)

            if eval_val < min_eval:
                min_eval = eval_val
                best_action = action

            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval, best_action


def get_best_action_minimax(state, time_limit=2.0):
    """
    Uses Iterative Deepening to search as deep as possible within the time limit.
    """
    start_time = time.time()
    best_action = None
    maximizing = (state.next_to_move == 1)

    try:
        for depth in range(1, 10):
            _, action = minimax_alpha_beta(state, depth, -float('inf'), float('inf'), maximizing, start_time,
                                           time_limit)
            if action is not None:
                best_action = action
    except TimeoutError:
        pass

    if best_action is None:
        legal = state.get_legal_actions()
        if legal:
            best_action = legal[0]

    return best_action