import copy, random

CARD_VALS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

#Base class
class Agent:
	def __init__(self, playerNum):
		self.playerNum = playerNum

	def getAction(self, moves, game):
		raise NotImplementedError("Override me")

	def getCall(self, game, verbose):
		raise NotImplementedError("Override me")

'''
Human agent, the person playing against our computers.
'''
class HumanAgent(Agent):
	def getAction(self, moves, game):
		hand = game.players[self.playerNum].hand
		formattedHand = []
		for i in range(len(hand)):
			if hand[i] != 0:
				for j in range(hand[i]):
					formattedHand.append(CARD_VALS[i])
		formattedHand = ', '.join(formattedHand)
		#print hand
		print "Your hand is: {}".format(formattedHand)
		while True:
			userMove = raw_input("Please input the cards you would like to play" + \
            					  ", separated by spaces: ")
			userMove = userMove.split()
			userMove = tuple(sorted([CARD_VALS.index(card) for card in userMove if card in CARD_VALS]))
			#print userMove
			if userMove not in moves:
				print "Please enter a valid move. Try again."
				continue
			else:
				return userMove

	def getCall(self, game, verbose):
		lastPlayer = (game.currPlayer - 1) % game.numPlayers
		if lastPlayer != self.playerNum:
			call = raw_input("Would you like to call BS?  Enter 'y' for yes " + \
							 "and 'n' for no. \nEnter choice: ")
			if call == 'y':
				if verbose:
					print "\nYou have called BS!"
				return True
			elif call == 'n':
				if verbose:
					print "\nYou have not called BS."
				return False
		else: 
			return False

'''
Random agent, plays a random move and chooses randomly wehter to call
BS on a player
'''
class RandomAgent(Agent):
    def getAction(self, moves, game):
        if moves:
            return random.choice(list(moves))
        return None

    def getCall(self, game, verbose):
    	lastPlayer = (game.currPlayer - 1) % game.numPlayers
    	if lastPlayer != self.playerNum:
	    	call = random.randint(0, 1)
	    	if call == 0:
			if verbose:
				print "Player {} does not call BS.".format(self.playerNum)
	    		return False
	    	else:
			if verbose:
				print "Player {} calls BS!".format(self.playerNum)
	    		return True
    	else:
	    	return False

'''
Only plays honestly, i.e. tries to never lie. If lying is inevitable, picks 1
card at random and plays it. Never calls in order to try and get rid of cards
as fast as possible (Trusts other players to be honest, often a bad idea).
'''
class HonestAgent(Agent):
	def getAction(self, moves, game):
		currCard = game.currCard
		honestMoves = []
		for move in moves:
			add = True
			for i in range(len(move)):
				if move[i] != currCard: add = False
			if add: honestMoves.append(move)

		# Must be dishonest, unfortunately
		if not honestMoves:
			singleMoves = []
			for move in moves:
				if len(move) == 1: singleMoves.append(move)
			return random.choice(list(singleMoves))
		# Can be honest!
		else:
			return max(honestMoves, key=lambda x: len(x))
		
	def getCall(self, game, verbose):
		lastPlayer = (game.currPlayer - 1) % game.numPlayers
		if lastPlayer != self.playerNum:
			if verbose:
				print "Player {} does not call BS.".format(self.playerNum)
			return False
	
"""
Similar to honestAgent, but always calls BS.
"""
class AlwaysCallBSAgent(Agent):
	def getAction(self, moves, game):
		currCard = game.currCard
		honestMoves = []
		for move in moves:
			add = True
			for i in range(len(move)):
				if move[i] != currCard: add = False
			if add: honestMoves.append(move)

		# Must be dishonest, unfortunately
		if not honestMoves:
			singleMoves = []
			for move in moves:
				if len(move) == 1: singleMoves.append(move)
			return random.choice(list(singleMoves))
		# Can be honest!
		else:
			return max(honestMoves, key=lambda x: len(x))
		
		
	def getCall(self, game, verbose):
		lastPlayer = (game.currPlayer - 1) % game.numPlayers
		if lastPlayer != self.playerNum:
			if verbose:
				print "Player {} calls BS!".format(self.playerNum)
			return True

"""
Dishonest "Greedy" agent, only plays dishonest, i.e. always lies and tries to get rid of
cards as greedily as possible. Never calls BS in order to get rid of cards as
quickly as possible.
"""
class DishonestAgent(Agent):
	def getAction(self, moves, game):
		currCard = game.currCard
		honestMoves = []
		maxLen = max(len(move) for move in moves)
		greedyMoves = []
		for move in moves:
			if len(move) == maxLen: greedyMoves.append(move)
		return random.choice(list(greedyMoves))
			
	def getCall(self, game, verbose):
		lastPlayer = (game.currPlayer - 1) % game.numPlayers
		if lastPlayer != self.playerNum:
			if verbose:
				print "Player {} does not call BS.".format(self.playerNum)
			return False

"""
TODO: Fix this
Takes in an evaluation function and selects best action to take based
on the value of the successor states. 
"""
class ReflexAgent(Agent):
	def __init__(self, playerNum, evalFunction, w=None):
		self.playerNum = playerNum
		self.evaluationFunction = evalFunction
		self.w = w

	def setWeights(self, w):
		self.w = w

	"""
	The value of an action is calculated as the average of the successor 
	state if someone calls BS and the successor state if someone does not
	call BS.
	"""
	def getAction(self, moves, game):
		#print "Original hand: {}".format(game.players[self.playerNum].hand)
		scoresActions = []
		for move in moves:
			g = game.clone()
			# print "Equal: ", game.players[self.playerNum].hand == g.players[self.playerNum].hand
			g.takeAction(move, self.playerNum)
			noCallScore = self.evaluationFunction((g, self.playerNum), self.w)
			# TODO: Change to reflect the turn-based call rule
			caller = random.choice([i for i in range(g.numPlayers) if i != self.playerNum])
			g.takeCall(caller)
			callScore = self.evaluationFunction((g, self.playerNum), self.w)
			# if sum(game.discard) > 4:
				# print "Original hand: ", game.players[self.playerNum].hand
				# print "Discard: ", game.discard
				# print "Hand: ", g.players[self.playerNum].hand
				# print "Move: ", move
				# print "Required card: ", game.currCard
				# print "Discard size: ", sum(game.discard)
				# print "No call score: ", noCallScore
				# print "Call score: ", callScore
				# print "\n"
			avgScore = 0.5 * noCallScore + 0.5 * callScore #Debug
			scoresActions.append((move, avgScore))
		action = max(scoresActions, key=lambda x: x[1])[0]
		return action

	# TODO: 
	def getCall(self, game, verbose):
		noCallScore = self.evaluationFunction((game, self.playerNum), self.w)

		# Scenario 1: Call BS incorrectly, add discard to self 
		g1 = game.clone()
		g1.addDiscard(self.playerNum)
		callScore1 = self.evaluationFunction((g1, self.playerNum), self.w)

		# Scenario 2: Call BS correctly, add discard to opponent
		g2 = game.clone()
		lastPlayer = (g2.currPlayer - 1) % g2.numPlayers
		g2.addDiscard(lastPlayer)
		callScore2 = self.evaluationFunction((g2, self.playerNum), self.w)

		# Average the scores of the two scenarios
		avgCallScore = 0.5 * callScore1 + 0.5 * callScore2 #Debug

		#print noCallScore, avgCallScore #Debug

		if noCallScore > avgCallScore:
			#print "Not calling!" #Debug
			if verbose:
				print "Player {} does not call BS.".format(self.playerNum)
			return False
		else:
			#print "Calling!" #Debug
			if verbose:
				print "Player {} calls BS!".format(self.playerNum)
			return True
