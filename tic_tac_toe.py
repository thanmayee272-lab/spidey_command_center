import random

# ============================================================================
# TIC-TAC-TOE
#
# GAME RULES:
#   - The board is a 3x3 grid. Cells are numbered 1-9 (like a phone keypad),
#     counting left-to-right, top-to-bottom.
#   - Two players take turns: YOU are 'X', the COMPUTER is 'O'.
#   - You always go first. On your turn you type the number (1-9) of an
#     empty cell to place your 'X' there.
#   - The computer then picks a random empty cell and places an 'O'.
#   - A player WINS the moment they get three of their marks in a straight
#     line. A line can be:
#         * any of the 3 rows       (horizontal)
#         * any of the 3 columns    (vertical)
#         * either of the 2 diagonals (corner-to-corner)
#   - If all 9 cells fill up and nobody has three-in-a-row, it's a DRAW.
#   - As soon as someone wins (or it's a draw), announce the result and stop.
#
#   Marks are permanent: once a cell has an X or an O, it can't be changed
#   or played again.
# ============================================================================

b = [str(i) for i in range(1, 10)]

over = False
turn = 0
while not over:
    print()
    r = 0
    while r < 3:
        line = ""
        c = 0
        while c < 3:
            line += " " + b[r*3+c] + " "
            if c < 2:
                line += "|"
            c += 1
        print(line)
        if r < 2:
            print("---+---+---")
        r += 1
    print()

    if turn % 2 == 0:
        got = False
        while not got:
            k = input("Your move (1-9): ")
            good = False
            for n in range(1, 10):
                if k == str(n):
                    good = True
            if not good:
                continue
            idx = int(k) - 1
            if b[idx] == 'X' or b[idx] == 'O':
                print("taken!")
                continue
            b[idx] = 'X'
            got = True
        m = 'X'
    else:
        opts = []
        i = 0
        while i < 9:
            if b[i] != 'X' and b[i] != 'O':
                opts.append(i)
            i += 1
        if len(opts) != 0:
            pick = opts[random.randint(0, len(opts) - 1)]
            b[pick] = 'O'
            print("Computer plays", pick + 1)
        m = 'O'

    w = False
    rr = 0
    while rr < 3:
        if b[rr*3] == m and b[rr*3+1] == m and b[rr*3+2] == m:
            w = True
        rr += 1
    cc = 0
    while cc < 3:
        z = 0
        ok = True
        while z < 3:
            if b[cc+z*3] != m:
                ok = False
            z += 1
        if ok:
            w = True
        cc += 1

    if w:
        print()
        p = 0
        while p < 3:
            line = ""
            q = 0
            while q < 3:
                line += " " + b[p*3+q] + " "
                if q < 2:
                    line += "|"
                q += 1
            print(line)
            if p < 2:
                print("---+---+---")
            p += 1
        print()
        if m == 'X':
            print("You win! :)")
        else:
            print("Computer wins! :/")
        over = True

    if not over:
        f = True
        j = 0
        while j < 9:
            if b[j] != 'X' and b[j] != 'O':
                f = False
            j += 1
        if f:
            print("It's a draw!")
            over = True

    turn += 1