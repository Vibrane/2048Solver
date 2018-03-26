from __future__ import print_function
import copy, random

MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}


class State:
    """game state information"""

    # Hint: probably need the tile matrix, which player's turn, score, previous move
    def __init__(self, matrix, player, score, pre_move, height): #initializing the constructor
        self.matrix = matrix  
        self.player = player
        self.score = score
        self.pre_move = pre_move
        self.children = []
        self.height = height

    def __gt__(self, other):  # For x > y  #overloading greather than
        return self.score > other.score

    def __eq__(self, other):  # For x == y #overloading equals to

        if ((id(self) == id(other)) or (self.score == other.score and self.matrix != other.matrix)):
            return True
        else:
            return False

    def highest_tile(self):  #finding the highest children tile
        maxChild = State(None, False, -1, None, -1)
        if (len(self.children) == 0):
            return None
        else:
            for child in self.children:
                if child > maxChild:
                    maxChild = child
        return maxChild


class GameTree:
    """main class for the AI"""

    # Hint: Two operations are important. Grow a game tree, and then compute minimax score.
    # Hint: To grow a tree, you need to simulate the game one step.
    # Hint: Think about the difference between your move and the computer's move.
    def __init__(self, matrix, totalPoints, depth):
        self.rootstate = State(matrix, True, totalPoints, None, 0) #initializing the rootstate
        self.depth = depth

    def grow_once(self, state, iteration): # grow_once iterative version b/c faster than recursive way
        if (iteration == 0):  # rootstate grow
            for i in range(0, 4):
                simulation = Simulator(copy.deepcopy(state.matrix), state.score)  # root
                if simulation.checkIfCanGo():
                    simulation.move(i)  # moves in the direction
                    childState = State(simulation.tileMatrix, False, simulation.total_points, i, state.height + 1)
                    if childState > state or childState == state:
                        state.children.append(childState)
        elif iteration == 1: # takes care of the computer move
            for child in state.children:
                for i in range(len(child.matrix)):
                    for j in range(len(child.matrix[i])):
                        if child.matrix[i][j] == 0:
                            matrix = copy.deepcopy(child.matrix)
                            score = child.score
                            preMove = child.pre_move
                            height = child.height
                            matrix[i][j] = 2
                            childState = State(matrix, True, score, preMove, height + 1)
                            child.children.append(childState)
        elif iteration == 2:
            for one in state.children:  # for all the children of the root
                for two in one.children:  # for each of the children of one
                    for i in range(0, 4):
                        simulation = Simulator(copy.deepcopy(two.matrix), two.score)
                        if simulation.checkIfCanGo():
                            simulation.move(i)
                            childState = State(simulation.tileMatrix, False, simulation.total_points, i, two.height + 1)
                            two.children.append(childState)
                            
    def grow(self, state, height):
        iteration = 0 #calling growOnce based on depth value
        while (0 <= iteration < height):
            self.grow_once(state, iteration)
            iteration += 1

    def expectimax(self, state):
        """Compute minimax values on the tree"""
        if (self.depth == 1):
            return state.highest_tile().pre_move
        elif (self.depth == 3):
            for child in state.children: #level 1
                score = 0
                count = 0
                for c in child.children: # level 2
                    if c.children != None:
                        for x in c.children:
                            score += x.score
                            count += 1
                if (count > 0): # checks count value
                    child.score = score / count # updates the score for each of the potential root children
            return state.highest_tile().pre_move

        return None

    def compute_decision(self): #figures out the decision
        """Derive a decision"""
        if (self.depth == 0):
            decision = self.randomMove()
        else:
            self.grow(self.rootstate, self.depth)
            decision = self.expectimax(self.rootstate)

        # Should also print the minimax value at the root
        print(MOVES[decision])
        return decision

    def randomMove(self):
        return random.randint(0, 3)


class Simulator:  # copied the game code 
    """Simulation of the game"""

    # Hint: You basically need to copy all the code from the game engine itself.
    # Hint: The GUI code from the game engine should be removed.
    # Hint: Be very careful not to mess with the real game states.
    def __init__(self, matrix, score):
        self.total_points = score
        self.board_size = 4
        self.tileMatrix = matrix
        self.undoMat = []

    def move(self, direction): # move in the direction specified 
        self.addToUndo()
        for i in range(0, direction):
            self.rotateMatrixClockwise()
        if self.canMove():
            self.moveTiles()
            self.mergeTiles()
        for j in range(0, (4 - direction) % 4):
            self.rotateMatrixClockwise()

    def moveTiles(self):
        tm = self.tileMatrix
        for i in range(0, self.board_size):
            for j in range(0, self.board_size - 1):
                while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
                    for k in range(j, self.board_size - 1):
                        tm[i][k] = tm[i][k + 1]
                    tm[i][self.board_size - 1] = 0

    def mergeTiles(self):
        tm = self.tileMatrix
        for i in range(0, self.board_size):
            for k in range(0, self.board_size - 1):
                if tm[i][k] == tm[i][k + 1] and tm[i][k] != 0:
                    tm[i][k] = tm[i][k] * 2
                    tm[i][k + 1] = 0
                    self.total_points += tm[i][k]
                    self.moveTiles()

    def checkIfCanGo(self):
        tm = self.tileMatrix
        for i in range(0, self.board_size ** 2):
            if tm[int(i / self.board_size)][i % self.board_size] == 0:
                return True
        for i in range(0, self.board_size):
            for j in range(0, self.board_size - 1):
                if tm[i][j] == tm[i][j + 1]:
                    return True
                elif tm[j][i] == tm[j + 1][i]:
                    return True
        return False

    # checks if can move
    def canMove(self):
        tm = self.tileMatrix
        for i in range(0, self.board_size):
            for j in range(1, self.board_size):
                if tm[i][j - 1] == 0 and tm[i][j] > 0:
                    return True
                elif (tm[i][j - 1] == tm[i][j]) and tm[i][j - 1] != 0:
                    return True
        return False

    def rotateMatrixClockwise(self): #dont care about this
        tm = self.tileMatrix
        for i in range(0, int(self.board_size / 2)):
            for k in range(i, self.board_size - i - 1):
                temp1 = tm[i][k]
                temp2 = tm[self.board_size - 1 - k][i]
                temp3 = tm[self.board_size - 1 - i][self.board_size - 1 - k]
                temp4 = tm[k][self.board_size - 1 - i]
                tm[self.board_size - 1 - k][i] = temp1
                tm[self.board_size - 1 - i][self.board_size - 1 - k] = temp2
                tm[k][self.board_size - 1 - i] = temp3
                tm[i][k] = temp4

    def convertToLinearMatrix(self):
        m = []
        for i in range(0, self.board_size ** 2):
            m.append(self.tileMatrix[int(i / self.board_size)][i % self.board_size])
        m.append(self.total_points)
        return m

    def addToUndo(self):
        self.undoMat.append(self.convertToLinearMatrix())

    def undo(self):
        if len(self.undoMat) > 0:
            m = self.undoMat.pop()
            for i in range(0, self.board_size ** 2):
                self.tileMatrix[int(i / self.board_size)][i % self.board_size] = m[i]
            self.total_points = m[self.board_size ** 2]
            self.printMatrix()
