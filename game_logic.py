def new_board() -> list:
    return [" "] * 9

def is_legal_move(board: list, cell: int) -> bool:
    if cell < 0 or cell > 8:
        return False
    if board[cell] != " ":
        return False
    return True

def make_move(board: list, cell: int, mark: str) -> list:
    new_board = board.copy()
    new_board[cell] = mark
    return new_board

def winner(board: list) -> str | None:
    winning_lines = [
        [0, 1, 2],  # top row
        [3, 4, 5],  # middle row
        [6, 7, 8],  # bottom row
        [0, 3, 6],  # left column
        [1, 4, 7],  # middle column
        [2, 5, 8],  # right column
        [0, 4, 8],  # diagonal
        [2, 4, 6]   # diagonal
    ]

    for line in winning_lines:
        first = line[0]
        second = line[1]
        third = line[2]
        if board[first] != " ":
            if board[first] == board[second] == board[third]:
                return board[first]
    return None

def is_full(board: list) -> bool:
    if " " not in board:
        return True
    return False

def game_state(board: list) -> str:
    if winner(board) == "X":
        return "X wins"
    if winner(board) == "O":
        return "O wins"
    if is_full(board):
        return "draw"
    
    return "in progress"