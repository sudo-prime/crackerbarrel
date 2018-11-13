from copy import copy, deepcopy
import argparse
import math

class Hole:
    def __init__(self, x, y):
        self.adjacent = {
            "upLeft"    : None,
            "upRight"   : None,
            "left"      : None,
            "right"     : None,
            "downLeft"  : None,
            "downRight" : None
        }
        self.hasPeg = True
        self.x = x
        self.y = y

class PegState:
    def __init__(self, graph, moves):
        self.graph = graph
        self.moves = moves
        
    def __copy__(self):
        return type(self)(deepcopy(self.graph), copy(self.moves))

    def print(self):
        print("0      {}    ".format("o" if self.graph[0][0].hasPeg else "."))
        print("1     {} {}  ".format("o" if self.graph[1][0].hasPeg else ".",
                                     "o" if self.graph[1][1].hasPeg else "."))
        print("2    {} {} {}".format("o" if self.graph[2][0].hasPeg else ".",
                                     "o" if self.graph[2][1].hasPeg else ".",
                                     "o" if self.graph[2][2].hasPeg else "."))
        print("3   {} {} {} {}".format("o" if self.graph[3][0].hasPeg else ".",
                                       "o" if self.graph[3][1].hasPeg else ".",
                                       "o" if self.graph[3][2].hasPeg else ".",
                                       "o" if self.graph[3][3].hasPeg else "."))
        print("4  {} {} {} {} {}".format("o" if self.graph[4][0].hasPeg else ".",
                                         "o" if self.graph[4][1].hasPeg else ".",
                                         "o" if self.graph[4][2].hasPeg else ".",
                                         "o" if self.graph[4][3].hasPeg else ".",
                                         "o" if self.graph[4][4].hasPeg else "."))
        print("  0 1 2 3 4")

    def constructStartState(self):
        # Create all hole objects
        for i in range(0, 5):
            row = []
            for j in range(0, i + 1):
                current = Hole(i, j)
                row.append(current)
            self.graph.append(row)
        
        # Link them together via fields
        for i in range(0, len(self.graph)):
            for j in range(0, len(self.graph[i])):
                hole = self.graph[i][j]
                if j > 0:
                    hole.adjacent["upLeft"] = self.graph[i-1][j-1]
                    hole.adjacent["left"]   = self.graph[i][j-1]
                if i - j > 0:
                    hole.adjacent["upRight"] = self.graph[i-1][j]
                    hole.adjacent["right"]   = self.graph[i][j+1]
                if i < 4:
                    hole.adjacent["downLeft"]  = self.graph[i+1][j]
                    hole.adjacent["downRight"] = self.graph[i+1][j+1]
        return self
    
    def countPegs(self):
        count = 0
        for i in range(0, 5):
            for j in range(0, i + 1):
                if self.graph[i][j].hasPeg: count += 1
        return count
    
    def findAllValidMoves(self):
        moves = []
        for i in range(0, 5):
            for j in range(0, i + 1):
                origin = self.graph[i][j]
                if origin.hasPeg:
                    for key in origin.adjacent.keys():
                        if origin.adjacent[key] != None:
                            if origin.adjacent[key].hasPeg and origin.adjacent[key].adjacent[key] != None:
                                if not origin.adjacent[key].adjacent[key].hasPeg:
                                    # Found a valid move!
                                    fromPos = (origin.x, origin.y)
                                    midPos  = (origin.adjacent[key].x, origin.adjacent[key].y)
                                    toPos   = (origin.adjacent[key].adjacent[key].x, origin.adjacent[key].adjacent[key].y)
                                    moves.append(Move(fromPos, midPos, toPos))
        return moves
    
    def perform(self, move):
        self.moves.append(move)
        origin = self.graph[move.fromPos[0]][move.fromPos[1]]
        middle = self.graph[move.midPos[0]][move.midPos[1]]
        target = self.graph[move.toPos[0]][move.toPos[1]]
        origin.hasPeg = False
        middle.hasPeg = False
        target.hasPeg = True
        return self

class Move():
    def __init__(self, fromPos, midPos, toPos):
        self.fromPos = fromPos
        self.midPos  = midPos
        self.toPos   = toPos

    def __str__(self):
        return "{}->{}".format(self.fromPos, self.toPos)

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

solutionsEncountered = 0

def solve(state, desiredSolution):
    global solutionsEncountered
    state.print()
    if state.countPegs() == 1:
        print("Found solution!")
        if solutionsEncountered != desiredSolution:
            solutionsEncountered += 1
            return None
        else:
            solutionsEncountered += 1
            return state
    moves = state.findAllValidMoves()
    print([(move.fromPos, move.toPos) for move in moves])
    if not moves: return None
    newStates = [copy(state).perform(move) for move in moves]
    for newState in newStates:
        result = solve(newState, desiredSolution)
        if result != None: return result

def solveAll(state):
    global solutionsEncountered
    if state.countPegs() == 1:
        solutionsEncountered += 1
        if solutionsEncountered % 1000 == 0:
            print("{} solutions counted so far.".format(solutionsEncountered))
        return None
    moves = state.findAllValidMoves()
    if not moves: return None
    newStates = [copy(state).perform(move) for move in moves]
    for newState in newStates:
        result = solveAll(newState)
        if result != None: return result

def manual(state):
    while state.countPegs() != 1:
        state.print()
        print("There are {} pegs remaining.".format(state.countPegs()))
        moves = state.findAllValidMoves()
        if not moves:
            print("No more moves, you lose! There were {} pegs left.".format(state.countPegs()))
            return
        movesReadable = ", ".join([str(move) for move in moves])
        print("The following moves are available: {}".format(movesReadable))
        pick = eval(input("Which move would you like to perform? [0-{}]: ".format(len(moves) - 1)))
        while pick < 0 or pick > len(moves) - 1:
            print("Input out of range.")
            print("The following moves are available: {}".format(movesReadable))
            pick = eval(input("Which move would you like to perform? [0-{}]: ".format(len(moves) - 1)))
        move = moves[pick]
        state.perform(move)
    state.print()
    print("You win! Well done, genius.")

def traverseMoves(state):
    moves = state.moves
    exampleState = PegState([], []).constructStartState()
    exampleState.graph[0][0].hasPeg = False
    while moves:
        move = moves.pop(0)
        exampleState.print()
        print("Next move to be performed: {}->{}. Press enter to continue.".format(move.fromPos, move.toPos))
        input("")
        exampleState.perform(move)
    exampleState.print()
    print("All done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cracker Barrel Puzzle Simulator")
    parser.add_argument('n', metavar='n', nargs='?', default=1, type=int, help='the solution you want to find')
    parser.add_argument('-s', '--solve', action='store_true', help='find nth solution automagically')
    parser.add_argument('-a', '--all', action='store_true', help='find all solutions and count them')
    args = parser.parse_args()

    startingState = PegState([], []).constructStartState()
    startingState.graph[0][0].hasPeg = False

    if args.all:
        solveAll(startingState)
        print("Counting the number of 1-peg solutions...")
        print("{} solutions found.".format(solutionsEncountered))
    elif args.solve:
        solutionState = solve(startingState, args.n - 1)
        print("\nI----------BEGIN SOLUTION PLAYBACK----------I\n")
        print("This is the {} solution.".format(ordinal(solutionsEncountered)))
        traverseMoves(solutionState)
    else:
        print("Manual mode. Specify --solve to find the first 1-peg solution,")
        print("--solve n to find the nth 1-peg solution, or --all to count all 1-peg solutions.")
        manual(startingState)
