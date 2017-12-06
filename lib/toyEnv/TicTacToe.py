import gym
import numpy as np
import pickle

ROWS_TRADITION = 3
COLS_TRADITION = ROWS_TRADITION
WIN_CONDITION = ROWS_TRADITION

'''
BoardEnv represents the current state of the game.
On every position (i, j) of the board: states[i, j] = 
	0 means it is empty;
	1 means it was chose by the first-move player;
	-1 means it was chose by the other player.
If the game meet and end: winner = 
	1 means the first-move player win;
	-1 means the other player win;
	0  means its a tie.
'''
class BoardEnv:
    rows = ROWS_TRADITION
    cols = COLS_TRADITION
    ruleWin = WIN_CONDITION
	# The board is represented by a rows * cols array.
    def __init__(self):
        if self.ruleWin > max(self.rows, self.cols):
            print "The win condition cannot reach"
        self.states = np.zeros((self.rows, self.cols))
        self.hashStates = None
        self.end = None
        self.winner = None

    # Give an unique hash value to every states
    # There are pow(3, rows * cols) states in total
    def getHash(self):
        if self.hashStates == None:
            self.hashStates = 0
            for i in self.states.reshape(self.rows * self.cols):
                if -1 == i:
                    i = 2
                self.hashStates = self.hashStates * 3 + i
        return int(self.hashStates)

    # A player have chose a position, the environment changed its state
    # (i, j) is the position on the board, and 'whichPlayer' has value -1 or 1
    def moveToNext(self, i, j, whichPlayer):
        if whichPlayer != 1 and whichPlayer != -1:
            print "Input error, no such player"
            return
        if self.states[i, j] != 0:
            print "Illegal Operation"
        else:
            self.states[i, j] = whichPlayer

    # See whether reach the end, and which player wins
    def isEnd(self):
        if self.end is not None:
            return self.end
        results = []
        # Check rows
        for i in range(0, self.rows):
            results.append(np.sum(self.states[i, :]))
        # Check columns
        for i in range(0, self.columns):
            results.append(np.sum(self.states[:, i]))
        # Check diagonals
        results.append(0)
        for i in range(0, self.rows):
            results[-1] += self.states[i,i]
        results.append(0)
        for i in range(0, self.rows):
            results[-1] += self.states[i, self.cols-1-i]

        for result in results:
            if result == self.ruleWin:
                self.winner = 1
                self.end = True
                return self.end
            if result == 0 - self.ruleWin:
                self.winner = -1
                self.end = True
                return self.end
        # Check whether it's a tie
        theSum = np.sum(np.abs(self.states))
        if theSum == self.rows * self.cols:
            self.winner = 0
            self.end = True
            return self.end

        # The game is still going on
        self.end = False
        return self.end

    # print the board
    def boardPrint(self):
        for i in range(0, self.rows):
            print '-------------'
            out = '| '
            for j in range(0, self.cols):
                if self.states[i, j] == 1:
                    token = 'O'
                elif self.states[i, j] == 0:
                    token = ' '
                else:
                    token = 'X'
                out += token + ' | '
            print(out)
        print '-------------'

'''
Judger works like a executor of the virtual environment and the its rules,
enable the interaction between players and the world. 
'''
class Judger:
    # @player1: the player who moves first
    # @player2: another player
    # @feedback: a boolean to decide whether to give palyer feedback at the end of each episode
    def __init__(self, player1, player2, feedback=True):
        self.p1 = player1
        self.p2 = player2
        self.feedback = feedback
        self.currentPlayer = None
        self.p1Symbol = 1
        self.p2Symbol = -1
        self.p1.setSymbol(self.p1Symbol)
        self.p2.setSymbol(self.p2Symbol)
        self.currentState = BoardEnv()

    def giveReward(self):
        if self.currentState.winner == self.p1Symbol:
            self.p1.feedReward(1)
            self.p2.feedReward(0)
        elif self.currentState.winner == self.p2Symbol:
            self.p1.feedReward(0)
            self.p2.feedReward(1)
        else:
            self.p1.feedReward(0.1)
            self.p2.feedReward(0.5)

    def reset(self):
        self.p1.reset()
        self.p2.reset()
        self.currentState = BoardEnv()
        self.currentPlayer = None

    # @show: Decide whether to print the board during the game
    def play(self, show=False):
        self.reset()
        while True:
            if self.currentPlayer == self.p1:
                self.currentPlayer == self.p2
            else:
                self.currentPlayer == self.p1
            if show:
                self.currentState.boardPrint()
            [i, j, symbol] = self.currentPlayer.takeAction()
            self.currentState = self.currentState.moveToNext(i, j, symbol)
            hashValue = self.currentState.getHash()
            self.currentState, isEnd = self.allStates[hashValue]
            self.feedCurrentState()
            if isEnd:
                if self.feedback:
                    self.giveReward()
                return self.currentState.winner 

# AI player
class Player:
    # @stepSize: step size to update estimations
    # @exploreRate: possibility to explore
    def __init__(self, stepSize = 0.1, exploreRate = 0.1):
        self.allStates = allStates
        self.estimations = dict()
        self.stepSize = stepSize
        self.exploreRate = exploreRate
        self.states = []

    def reset(self):
        self.states = []

    def setSymbol(self, symbol):
        self.symbol = symbol
        for i in self.allStates.keys():
            (state, isEnd) = self.allStates[i]
            if isEnd:
                if state.winner == self.symbol:
                    self.estimations[i] = 1.0
                else:
                    self.estimations[i] = 0
            else:
                self.estimations[i] = 0.5

    def feedState(self, state):
        self.states.append(state)

    def feedReward(self, reward):
        if len(self.states) == 0:
            return
        self.states = [state.getHash() for state in self.states]
        target = reward
        for latestState in reversed(self.states):
            value = self.estimations[latestState] + self.stepSize * (target - self.estimations[latestState])
            self.estimations[latestState] = value
            target = value
        self.states = []

    def takeActions(self):
        state = self.states[-1]
        nextStaes = []
        nextPositions = []
        for i in range(BoardEnv.rows):
            for j in range(BoardEnv.cols):
                if state.data[i, j] == 0:
                    nextPositions.append([i, j])
                    nextStaes.append(state.nextStaes(i, j, self.symbol).getHash())
        if np.random.binomial(1, self.exploreRate):
            np.random.shuffle(nextPositions)
            self.states = []
            action = nextPositions[0]
            action.append(self.symbol)
            return action

        value = []
        for ha, pos in zip(nextStaes, nextPositions):
            values.append((self.estimations[ha], pos))
        np.random.shuffle(values)
        values.sort(key=lambda x:x[0], reverse=True)
        action = values[0][1]
        action.append(self.symbol)
        return action

    def savePolicy(self):
        fw = open('optimal_policy_' + str(self.symbol), 'wb')
        pickle.dump(self.estimations, fw)
        fw.close()

    def loadPolicy(self):
        fr = open('optimal_policy_' + str(self.symbol), 'rb')
        self.estimations = pickle.load(fr)
        fr.close()

# human interface
# input a number to put a chessman
# | 1 | 2 | 3 |
# | 4 | 5 | 6 |
# | 7 | 8 | 9 |
class HumanPlayer:
    def __init__(self, stepSize = 0.1, exploreRate=0.1):
        self.symbol = None
        self.currentState = None
        return
    def reset(self):
        return
    def setSymbol(self, symbol):
        self.symbol = symbol
        return
    def feedState(self, state):
        self.currentState = state
        return
    def feedReward(self, reward):
        return
    def takeAction(self):
        data = int(input("Input your position:"))
        data -= 1
        i = data // int(BoardEnv.cols)
        j = data % BoardEnv.cols
        if self.currentState.data[i, j] != 0:
            return self.takeAction()
        return (i, j, self.symbol)

def train(epochs = 20000):
    player1 = Player()
    player2 = Player()
    judger = Judger(player1, player2)
    player1Win = 0.0
    player2Win = 0.0
    for i in range(0, epochs):
        print("Epoch", i)
        winner = judger.play()
        if winner == 1:
            player1Win += 1
        if winner == -1:
            player2Win += 1
        judger.reset()
    print(player1Win / epochs)
    print(player2Win / epochs)
    player1.savePolicy()
    player2.savePolicy()

def compete(turns=500):
    player1 = Player(exploreRate=0)
    player2 = Player(exploreRate=0)
    judger = Judger(player1, player2, False)
    player1.loadPolicy()
    player2.loadPolicy()
    player1Win = 0.0
    player2Win = 0.0
    for i in range(0, turns):
        print("Epoch", i)
        winner = judger.play()
        if winner == 1:
            player1Win += 1
        if winner == -1:
            player2Win += 1
        judger.reset()
    print(player1Win / turns)
    print(player2Win / turns)

def play():
    while True:
        player1 = Player(exploreRate=0)
        player2 = HumanPlayer()
        judger = Judger(player1, player2, False)
        player1.loadPolicy()
        winner = judger.play(True)
        if winner == player2.symbol:
            print("Win!")
        elif winner == player1.symbol:
            print("Lose!")
        else:
            print("Tie!")

theEnv = BoardEnv()
theEnv.moveToNext(1,1,-1)
theEnv.moveToNext(1,2,1)
theEnv.boardPrint()
print theEnv.getHash()
