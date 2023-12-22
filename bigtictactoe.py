# an attempt at an implementation of alpha-beta minimax search
# this attempt is for ultimate tictactoe
import numpy as np
import copy


class Smallboard:
    def __init__(self):
        self.state = np.array(((None, None, None), (None, None, None), (None, None, None)))
        self.winner = None

    def move(self, x, y, player):
        if self.winner is not None:
            raise RuntimeError("Tried to move but this board is finished.")
        self.state[x][y] = player
        self.checkwin()

    def checkwin(self):
        for i in range(3):
            if self.state[i][0] == self.state[i][1] == self.state[i][2] is not None:
                self.winner = self.state[i][0]
                return
            if self.state[0][i] == self.state[1][i] == self.state[2][i] is not None:
                self.winner = self.state[0][i]
                return
        if self.state[0][0] == self.state[1][1] == self.state[2][2] is not None:
            self.winner = self.state[1][1]
            return
        if self.state[0][2] == self.state[1][1] == self.state[2][0] is not None:
            self.winner = self.state[1][1]
            return

    def __repr__(self):
        return f"{self.state[0][0]} {self.state[0][1]} {self.state[0][2]}\n{self.state[1][0]} {self.state[1][1]} {self.state[1][2]}\n{self.state[2][0]} {self.state[2][1]} {self.state[2][2]}"


class Bigboard:
    def __init__(self):
        self.state = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for i in range(3):
            for j in range(3):
                self.state[i][j] = Smallboard()
        self.state = np.array(self.state)
        self.next_big = [-1, -1]
        self.current_player = True
        self.winner = None

    def move(self, big_x, big_y, small_x, small_y, player, simulated=False):
        if self.winner is not None:
            if self.winner is True:
                print("Player 1 (X) has won!")
                return False
            else:
                print("Player 2 (O) has won!")
                return False
        if self.current_player is not player:
            print("It's not your turn.")
            return False
        if self.state[big_x][big_y].winner is not None:
            print("This sub-board was already won. Please move somewhere else.")
        if big_x != self.next_big[0] or big_y != self.next_big[1]:
            if self.next_big[0] != -1:
                print(big_x, big_y, small_x, small_y)
                print(f"You can't move in that big square. Move in ({self.next_big[0]}, {self.next_big[1]}) instead.")
                return False
        if self.state[big_x][big_y].state[small_x][small_y] is not None:
            print(big_x, big_y, small_x, small_y)
            print("That square is not empty. Try again.")
            return False
        self.state[big_x][big_y].move(small_x, small_y, player)
        self.next_big = [small_x, small_y]
        if self.state[small_x][small_y].winner is not None:
            self.next_big = [-1, -1]
        self.current_player = not self.current_player
        self.checkwin(simulated)
        return True  # returns true only if a move was successfully completed

    def get_possible_moves(self):
        moves = []
        if self.winner is not None:
            return []
        leave = True
        for i in range(9):
            if self.state[int(i/3)][i%3] is None:
                leave = False
        if leave:
            return []
        if self.next_big[0] != -1:
            small_board = self.state[self.next_big[0]][self.next_big[1]]
            for i in range(3):
                for j in range(3):
                    if small_board.state[i][j] is None:
                        moves.append([self.next_big[0], self.next_big[1], i, j])
        else:
            for i in range(3):
                for j in range(3):
                    small_board = self.state[i][j]
                    if small_board.winner is not None:
                        continue
                    for k in range(3):
                        for l in range(3):
                            if small_board.state[k][l] is None:
                                moves.append([i, j, k, l])
        return moves

    def checkwin(self, simulated):
        for i in range(3):
            if self.state[i][0].winner == self.state[i][1].winner == self.state[i][2].winner is not None:
                self.winner = self.state[i][0].winner
            if self.state[0][i].winner == self.state[1][i].winner == self.state[2][i].winner is not None:
                self.winner = self.state[0][i].winner
        if self.state[0][0].winner == self.state[1][1].winner == self.state[2][2].winner is not None:
            self.winner = self.state[1][1].winner
        if self.state[0][2].winner == self.state[1][1].winner == self.state[2][0].winner is not None:
            self.winner = self.state[1][1].winner
        if self.winner is not None and simulated is False:
            if self.winner is True:
                print("Player 1 (X) has won!")
            else:
                print("Player 2 (O) has won!")
        return

    def __repr__(self):
        string = ""
        for j in range(9):
            for i in range(9):
                winner = self.state[int(i/3)][int(j/3)].winner
                if winner is not None:
                    if i % 3 == 1 and j % 3 == 1:
                        if winner is True:
                            string += "X "
                        else:
                            string += "O "
                    else:
                        string += "  "
                    continue
                state = self.state[int(i/3)][int(j/3)].state[i%3][j%3]
                if state is None:
                    if int(i/3) == self.next_big[0] and int(j/3) == self.next_big[1]:
                        string += "? "
                    else:
                        string += "_ "
                elif state is True:
                    string += "X "
                else:
                    string += "O "
            string += "\n"
        return string


class Node:
    def __init__(self, position):
        self.previous_move = None
        self.children = []
        self.position = position
        self.terminal = False
        self.evaluation = -2**62  # evaluation can be considered really bad if we know nothing about it

    def evaluate(self, maximizing_player):  # maximizing player in here to make sure the evaluation is flipped for minimax if it's good for False
        # Evaluate board here
        # Idea: Bigboard matrix is center > corners > edges for values --> multipliers 2, 3, 4 (these can be adjusted to see if results change
        # Smallboard is same but modifier for whatever bigboard it's in --> multipliers 1, 2, 3 (can also be adjusted)
        score = 0
        for i in range(3):
            for j in range(3):  # i, j are bigboard coords
                if i == j == 1:
                    multiplier = 4
                elif (i+j) % 2 == 1:
                    multiplier = 2
                else:
                    multiplier = 3
                if self.position.state[i][j].winner is True:
                    score += multiplier * 10
                    continue
                if self.position.state[i][j].winner is False:
                    score -= multiplier * 10
                    continue
                for k in range(3):
                    for l in range(3):  # k, l are smallboard coords:
                        if k == l == 1:
                            multiplier *= 3
                        elif (l + l) % 2 == 1:
                            multiplier *= 1
                        else:
                            multiplier *= 2
                        # Add score now depending on who owns the square
                        owner = self.position.state[i][j].state[k][l]
                        if owner is None:
                            continue
                        elif owner is True:
                            score += multiplier  # positive evaluation means True is winning
                        else:
                            score -= multiplier  # negative evaluation means False is winning
        if self.position.winner is True:
            return 2*62  # large score since True won
        if self.position.winner is False:
            return -2**62  # small score since False won
        if maximizing_player is False:
            score *= -1
        self.evaluation = score
        return score

    def generate_children(self):
        moves = self.position.get_possible_moves()
        if len(moves) == 0:
            self.terminal = True
            return
        for move in moves:
            new_board = copy.deepcopy(self.position)
            new_board.move(move[0], move[1], move[2], move[3], new_board.current_player, True)
            new_node = Node(new_board)
            new_node.previous_move = move
            self.children.append(new_node)


# Minimax search with alpha-beta pruning:
# alpha = minimum score for maximizing player <--want to get this large, so start at -infinity
# beta = maximum score for minimizing player <-- want to get this small, so start at +infinity
# --> adjust alpha to the minimum of moves possible when looking at maximizing player's moves
# --> adjust beta to maximum of moves possible when looking at minimizing player's moves
def minimax(node, depth, alpha, beta, is_maximizing_player, maximizing_player):
    if depth <= 0:
        return node.evaluate(maximizing_player)
    node.generate_children()
    if node.terminal is True:
        return node.evaluate(maximizing_player)
    if len(node.children) == 0:
        raise RuntimeError("Wtf it's zero depth")
    if 0 < len(node.children) < 3:
        depth += 1  # basically if the search doesn't have that many possible moves, increase the depth
    if is_maximizing_player:
        value = -2**62
        for child in node.children:
            value = max(value, minimax(child, depth-1, alpha, beta, False, maximizing_player))
            if value > beta:
                break
            alpha = max(alpha, value)
        node.evaluation = value
        return value
    else:
        value = 2**62
        for child in node.children:
            value = min(value, minimax(child, depth-1, alpha, beta, True, maximizing_player))
            if value < alpha:
                break
            beta = min(beta, value)
        node.evaluation = value
        return value


def move_sequence_test(index, board):
    if index == 0:
        board.move(0, 0, 2, 0, True)
        board.move(2, 0, 0, 0, False)
        board.move(0, 0, 1, 0, True)
        board.move(1, 0, 0, 0, False)
        board.move(0, 0, 0, 0, True)
        board.move(1, 0, 1, 1, False)
        board.move(1, 1, 2, 1, True)
        board.move(2, 1, 1, 1, False)
        board.move(1, 1, 0, 1, True)
        board.move(0, 1, 1, 1, False)
        board.move(1, 1, 1, 1, True)
        board.move(2, 1, 2, 2, False)
        board.move(2, 2, 0, 2, True)
        board.move(0, 2, 2, 2, False)
        board.move(2, 2, 1, 2, True)
        board.move(1, 2, 2, 2, False)
        board.move(2, 2, 2, 2, True)
        board.move(0, 2, 2, 0, False)


class Machine:
    def __init__(self, player=False, depth=3):
        self.player = player
        self.depth = depth

    def find_move(self, position):
        root = Node(position)
        minimax(root, self.depth, -2**62, 2**62, True, self.player)
        move_tup = [[-1, -1, -1, -1], -2**62]  # void move with bad eval
        for child in root.children:
            if child.evaluation > move_tup[1]:
                move_tup = [child.previous_move, child.evaluation]
        print(f"Current evaluation for machine: {move_tup[1]}")
        return move_tup[0]


class Game:
    def __init__(self):
        self.board = Bigboard()
        self.move = 0

    def play(self):
        # Player 1 will be a real player (player True, X's)
        # Player 2 will be a machine (player False, O's)
        machine = Machine(False, 4)
        while self.board.winner is None:
            while True:  # Player's move
                string = input("Where do you wish to play? [bigX bigY smallX smallY] ")
                move = string.split()
                for i in range(len(move)):
                    move[i] = int(move[i])
                if len(move) != 4:
                    print("That's an invalid move format, try again")
                    continue
                if self.board.move(move[0], move[1], move[2], move[3], True) is True:
                    break
                else:
                    print("That's an invalid move location, try again")
            print(self.board)
            move = machine.find_move(self.board)
            self.board.move(move[0], move[1], move[2], move[3], False)
            print(self.board)


if __name__ == "__main__":
    game = Game()
    game.play()
