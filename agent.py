import random

CARD_VALS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

class Agent:

	def __init__(self, playerNum):
		self.playerNum = playerNum

	def getAction(self, moves, game):
		raise NotImplementedError("Override me")

	def getCall(self, game):
		raise NotImplementedError("Override me")

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
	    		return False
	    	else: 
	    		return True
    	else:
	    	return False

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
				return True
			elif call == 'n':
				return False
		else: 
			return False

