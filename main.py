from game_logic import new_board
from game_logic import is_legal_move
from game_logic import make_move
from game_logic import game_state

def render(board: list) -> str:
    board_text = (
        " " + board[0] + " | " + board[1] + " | " + board[2] + "\n"
        "---+---+---\n"
        " " + board[3] + " | " + board[4] + " | " + board[5] + "\n"
        "---+---+---\n"
        " " + board[6] + " | " + board[7] + " | " + board[8]
    )
    return board_text

def read_move(board: list, mark: str) -> int:
    while True:
        user_input = input(mark + "'s turn. Enter a cell (0-8): ")
        if not user_input.isdigit():
            print("Please enter a number from 0 to 8.")
            continue
        cell = int(user_input)
        if is_legal_move(board, cell):
            return cell
        print("That move is not legal. Try again.")

def main() -> None:
    board = new_board()
    mark = "X"
    while True:
        print()
        print(render(board))
        cell = read_move(board, mark)
        board = make_move(board, cell, mark)
        state = game_state(board)
        if state != "in progress":
            print()
            print(state)
            break
        if mark == "X":
            mark = "O"
        else:
            mark = "X"

main()