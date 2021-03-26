import numpy as np
import requester as req
from copy import deepcopy
from collections import Counter
import time
from helper import kth_diag_indices


class Game:
    def __init__(self, n, m):
        self.n = n
        self.target = m
        self.curr_board_state = np.full([n, n], ".")
        self.copy_board_state = np.full([n, n], ".")
        self.nmoves = 0

    def draw_board(self):
        for row in range(self.n):
            r = ''
            for column in range(self.n):
                r = r + f" {self.curr_board_state[row][column]} |"
            print(r)

    def is_tie(self, board):
        num=0
        for i in range(0, self.n):
            for j in range(0, self.n):
                if board[i][j] != '.':
                    num+=1
        if num == self.n * self.n:
            return True
        return False
    
    def heuristics(self):
        cons_x_row = 0
        cons_x_col = 0
        cons_x_diag = 0
        cons_y_row = 0
        cons_y_col = 0
        cons_y_diag = 0
        for i in range(0, self.n):
            for j in range(0, self.n - 1):
                if (
                    self.copy_board_state[i][j] == self.copy_board_state[i][j + 1]
                    and self.copy_board_state[i][j] == "X"
                    and (Counter(self.copy_board_state[i])['X'] + Counter(self.copy_board_state[i])['.']) == self.target
                ):
                    cons_x_row += 1

                elif (
                    self.copy_board_state[i][j] == self.copy_board_state[i][j + 1]
                    and self.copy_board_state[i][j] == "O"
                    and (Counter(self.copy_board_state[i])['O'] + Counter(self.copy_board_state[i])['.']) == self.target
                ):
                    cons_y_row += 1

        for i in range(0, self.n - 1):
            for j in range(0, self.n):
                if (
                    self.copy_board_state[i][j] == self.copy_board_state[i + 1][j]
                    and self.copy_board_state[i][j] == "X"
                    and (Counter(self.copy_board_state[:, j])['X'] + Counter(self.copy_board_state[:, j])['.']) == self.target
                ):
                    cons_x_col += 1
                elif (
                    self.copy_board_state[i][j] == self.copy_board_state[i + 1][j]
                    and self.copy_board_state[i][j] == "O"
                    and (Counter(self.copy_board_state[:, j])['O'] + Counter(self.copy_board_state[:, j])['.']) == self.target
                ):
                    cons_y_col += 1
        
        for i in range(self.copy_board_state.shape[1]):
            diag = np.diagonal(self.copy_board_state, offset = i)
            non_main_diag = np.diagonal(self.copy_board_state, offset=i, axis1=1, axis2=0)
            flip_main_diag = np.flipud(self.copy_board_state).diagonal(offset=i)
            flip_non_main_diag = np.flipud(self.copy_board_state).diagonal(offset=i, axis1=1, axis2=0)

            if len(diag) >= self.target and 'O' not in diag:
                cons_x_diag += 1
            if len(flip_main_diag) >= self.target and 'O' not in flip_main_diag:
                cons_x_diag += 1
            if len(non_main_diag) >= self.target and 'O' not in non_main_diag:
                cons_x_diag += 1
            if len(flip_non_main_diag) >= self.target and 'O' not in flip_non_main_diag:
                cons_x_diag += 1
            if len(diag) >= self.target and 'X' not in diag:
                cons_y_diag += 1
            if len(flip_main_diag) >= self.target and 'X' not in flip_main_diag:
                cons_y_diag += 1
            if len(non_main_diag) >= self.target and 'X' not in non_main_diag:
                cons_y_diag += 1
            if len(flip_non_main_diag) >= self.target and 'X' not in flip_non_main_diag:
                cons_y_diag += 1

        if max(cons_x_row, cons_x_col, cons_x_diag) > max(cons_y_row, cons_y_col, cons_y_diag):
            return (1, 0, 0)
        elif max(cons_x_row, cons_x_col, cons_x_diag)< max(cons_y_row, cons_y_col, cons_y_diag):
            return (-1, 0, 0)
        else:
            return (0, 0, 0)

    def is_won(self, player, board):
        is_won = False
        for indexes in self.check_indexes(self.n):
            cnt = 0
            for r, c in indexes:
                if board[r][c] == player:
                    cnt += 1
                else:
                    cnt = 0
                if cnt == self.target:
                    is_won = True
        if is_won and player == 'X':
            return (1, 0, 0)
        if is_won and player == 'O':
            return (-1, 0, 0)

    def is_end_of_game(self, depth: int, board):
        if self.is_tie(board):
            return True
        elif self.is_won("X", board) is not None:
            return True
        elif self.is_won("O", board) is not None:
            return True
        elif depth == 0:
            return True
        return False

    def check_indexes(self, n):
        for r in range(n):
            yield [(r, c) for c in range(n)]
        for c in range(n):
            yield [(r, c) for r in range(n)]
        diag_idx = []
        for i in range(self.target - self.n, n):
            r, c = kth_diag_indices(self.curr_board_state, i)
            if len(r) >= self.target:
                for k in range(0, len(r)):
                    diag_idx.append((r[k], c[k]))
        yield diag_idx


    def max_value(self, alpha: float, beta: float, depth: int) -> tuple:
        """Player X, i.e. AI."""
        max_value = -2
        # initialize maximizer's coordinates
        max_x, max_y = None, None

        if self.is_end_of_game(depth, self.copy_board_state):
            if self.is_tie(self.copy_board_state):
                return (0,0,0)
            elif self.is_won("X", self.copy_board_state) is not None:
                return self.is_won("X", self.copy_board_state)
            elif self.is_won("O", self.copy_board_state) is not None:
                return self.is_won("O", self.copy_board_state)
            else:
                return self.heuristics()

        for i in range(0, self.n):
            for j in range(0, self.n):
                # if empty, make a move and call minimizer
                if self.copy_board_state[i][j] == '.':
                    self.copy_board_state[i][j] = "X"
                    v, min_x, min_y = self.min_value(alpha, beta, depth - 1)

                    # maximize further
                    if v > max_value:
                        max_value = v
                        max_x = i
                        max_y = j
                    # undo move
                    self.copy_board_state[i][j] = '.'
                    # print(max_value, beta, alpha)
                    # stop examining moves, if current value better than beta
                    if max_value >= beta:
                        return max_value, max_x, max_y
                    # update alpha if current value is less
                    if max_value > alpha:
                        alpha = max_value

        return max_value, max_x, max_y

    def min_value(self, alpha: float, beta: float, depth: int) -> tuple:
        """Player O, i.e. our code."""
        min_value = 2
        # initialize minimizer's coordinates
        min_x, min_y = None, None

        if self.is_end_of_game(depth, self.copy_board_state):
            if self.is_tie(self.copy_board_state):
                return (0,0,0)
            elif self.is_won("X", self.copy_board_state) is not None:
                return self.is_won("X", self.copy_board_state)
            elif self.is_won("O", self.copy_board_state) is not None:
                return self.is_won("O", self.copy_board_state)
            else:
                return self.heuristics()

        for i in range(0, self.n):
            for j in range(0, self.n):
                # if empty, make a move and call maximizer
                if self.copy_board_state[i][j] == '.':
                    self.copy_board_state[i][j] = "O"
                    v, max_x, max_y = self.max_value(alpha, beta, depth - 1)

                    # minimize further
                    if v < min_value:
                        min_value = v
                        min_x = i
                        min_y = j
                    # undo move
                    self.copy_board_state[i][j] = '.'   

                    # stop examining moves, if current value is already less than alpha
                    if min_value <= alpha:
                        return min_value, min_x, min_y
                    # update beta if current value is less
                    if min_value < beta:
                        beta = min_value

        return min_value, min_x, min_y


def play_game(opponent_team_id: int, n: int, m: int):
    """Play the game."""
    max_depth = 3
    game = Game(n=n, m=m)
    while not game.is_end_of_game(max_depth, game.curr_board_state):
        game.copy_board_state = deepcopy(game.curr_board_state)
        min_value, min_x, min_y = game.min_value(alpha=-2, beta=2, depth = max_depth)
        if game.curr_board_state[min_x][min_y] != '.':
            print("Incorrect move made by your code!")
            break
        print("O makes this move: {}, {}".format(min_x, min_y))
        game.curr_board_state[min_x][min_y] = "O"
        game.nmoves += 1
        game.draw_board()
        if game.is_end_of_game(max_depth, game.curr_board_state):
            break
        x, y = input("Enter x and y for oppo: ").split()
        x = int(x)
        y = int(y)
        if game.curr_board_state[x][y] != '.':
            print("Incorrect move made by opponent!")
            break
        print("X makes this move: {}, {}".format(x, y))
        game.curr_board_state[x][y] = "X"
        game.nmoves += 1
        game.draw_board()
        # max_depth = max_depth - 1

    if game.is_end_of_game(max_depth, game.curr_board_state):
        print("Game over!")
        if game.is_won("X", game.curr_board_state) is not None:
            print("X won!")
        elif game.is_won("O", game.curr_board_state) is not None:
            print("O won!")
        elif game.is_tie(game.curr_board_state):
            print("Tie!")


        game.draw_board()


if __name__ == "__main__":

    # add exception handlers later
    opponent_team_id = int(input("Please enter opponent team id: \n"))
    n, m = input("Enter n and m for an n x n game with target m: ").split()
    play_game(opponent_team_id, int(n), int(m))