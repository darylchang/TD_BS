import random

CARD_VALS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

#Base class
class Agent:
	def __init__(self, playerNum):
		self.playerNum = playerNum

	def getAction(self, moves, game):
		raise NotImplementedError("Override me")

	def getCall(self, game):
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

	def getCall(self, game):
		lastPlayer = (game.currPlayer - 1) % game.numPlayers
		if lastPlayer != self.playerNum:
			call = raw_input("Would you like to call BS?  Enter 'y' for yes " + \
							 "and 'n' for no. If you call BS, you will be randomly " + \
							 "selected among the callers for BS.\nEnter choice: ")
			if call == 'y':
				print "\nYou have called BS!"
				return True
			elif call == 'n':
				print "\nYou have not called BS."
				return False
		else: 
			return False

class RandomAgent(Agent):
    def getAction(self, moves, game):
        if moves:
            return random.choice(list(moves))
        return None

    def getCall(self, game):
    	lastPlayer = (game.currPlayer - 1) % game.numPlayers
    	if lastPlayer != self.playerNum:
	    	call = random.randint(0, 1)
	    	if call == 0:
			print "Player {} does not call BS.".format(self.playerNum)
	    		return False
	    	else:
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

		#Must be dishonest, unfortunately
		if not honestMoves:
			singleMoves = []
			for move in moves:
				if len(move) == 1: singleMoves.append(move)
			return random.choice(list(singleMoves))
		#Can be honest!
		else:
			return max(honestMoves, key=lambda x: len(x))
		
		
	def getCall(self, game):
		lastPlayer = (game.currPlayer - 1) % game.numPlayers
		if lastPlayer != self.playerNum:
			print "Player {} does not call BS.".format(self.playerNum)
			call = 'n'
			return False

#TODO: Fill this in
class DishonestAgent(Agent):
	def getAction(self, moves, game):
		pass
	
	def getCall(self, game):
		pass

#TODO: Fill this in
class GreedyAgent(Agent):
	def getAction(self, moves, game):
		pass
	
	def getCall(self, game):
		pass

#TODO: Fill this in
class TDAgent(Agent):
	def getAction(self, moves, game):
		pass
	
	def getCall(self, game):
		pass
	
#TODO: Fill this in
class MinimaxAgent(Agent):
	def getAction(self, moves, game):
		pass
	
	def getCall(self, game):
		pass
	
#TODO: Fill this in
class ExpectimaxAgent(Agent):
	def getAction(self, moves, game):
		pass
	
	def getCall(self, game):
		pass