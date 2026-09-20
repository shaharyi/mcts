import time
import numpy as np

def evaluate_grid(grid):
    """Evaluates a single 3x3 grid (can be a micro-board or the main macro-board)"""
    score = 0
    # Define all 8 winning lines (3 rows, 3 cols, 2 diagonals)
    lines = [
        grid[0, :], grid[1, :], grid[2, :], 
        grid[:, 0], grid[:, 1], grid[:, 2], 
        grid.diagonal(), np.fliplr(grid).diagonal()
    ]
    
    for line in lines:
        s = sum(line)
        # If the line is won
        if s == 3: return 100
        if s == -3: return -100
        
        # Two in a row with an empty space
        zeros = np.count_nonzero(line == 0)
        if s == 2 and zeros == 1: score += 10
        if s == -2 and zeros == 1: score -= 10
        
        # One piece with two empty spaces
        if s == 1 and zeros == 2: score += 1
        if s == -1 and zeros == 2: score -= 1
            
    return score

def static_evaluation(state):
    """Scores the entire Ultimate Tic-Tac-Toe board."""
    if state.is_game_over():
        if state.game_result == 1: return 100000
        elif state.game_result == -1: return -100000
        else: return 0  # Draw

    score = 0
    main = state.main_board()
    
    # The macro board is the most important (x100 multiplier)
    score += evaluate_grid(main) * 100

    # Evaluate the individual micro boards
    for r in range(3):
        for c in range(3):
            # Only waste time evaluating micro boards that haven't been won yet
            if main[r, c] == 0:
                micro_score = evaluate_grid(state.board[r, c])
                
                # Center micro-board is slightly more valuable
                if r == 1 and c == 1:
                    micro_score *= 1.5
                    
                score += micro_score
                
    return score

def minimax_alpha_beta(state, depth, alpha, beta, maximizing_player, start_time, time_limit):
    """Recursive Alpha-Beta Pruning with a strict timeout."""
    # Prevent server hanging by enforcing the timeout
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
                break # Beta cutoff
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
                break # Alpha cutoff
        return min_eval, best_action

def get_best_action_minimax(state, time_limit=2.0):
    """
    Uses Iterative Deepening to search as deep as possible within the time limit.
    This guarantees a fast response for Flask, even on free hosting!
    """
    start_time = time.time()
    best_action = None
    maximizing = (state.next_to_move == 1)

    try:
        # Progressively search deeper. Will usually hit depth 4 or 5 before timeout.
        for depth in range(1, 10):
            _, action = minimax_alpha_beta(state, depth, -float('inf'), float('inf'), maximizing, start_time, time_limit)
            if action is not None:
                best_action = action
    except TimeoutError:
        pass # Time is up! Return the best action found from the previous completed depth.

    # Ultimate fallback just in case the server was too slow to even finish depth 1
    if best_action is None:
        best_action = np.random.choice(state.get_legal_actions())
        
    return best_action