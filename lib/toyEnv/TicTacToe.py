import gym
import numpy as np

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

theEnv = BoardEnv()
theEnv.moveToNext(1,1,-1)
theEnv.moveToNext(1,2,1)
theEnv.boardPrint()
print theEnv.getHash()
