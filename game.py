from player import Player
import copy, itertools, random

CARD_VALS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

class Game:

	def __init__(self, numPlayers=3, numDecks=1):
		self.players = [Player(i) for i in range(numPlayers)]
		self.numPlayers = numPlayers
		self.numDecks = numDecks
		self.currPlayer = 0
		self.currCard = 0
		self.lastAction = []
		self.discard = [0 for _ in range(13)]
		self.dealCards()
		self.candidateMoves = []

		# Create all possible moves
		cards = [i for i in range(13)]
		for i in range(1, 5):
			self.candidateMoves += list(itertools.product(cards, repeat=i))

	def dealCards(self):
		# Create deck of cards
		deck = []
		for i in range(4 * self.numDecks):
			for j in range(13):
				deck.append(j)
		random.shuffle(deck)
		
		# Separate into hands
		handSize = 52 / len(self.players)
		hands = []
		for i in range(len(self.players)):
			if i != len(self.players) - 1:
				hand = deck[i * handSize : (i+1) * handSize]
			else: 
				hand = deck[i * handSize: 52]
			hands.append(hand)
		random.shuffle(hands)

		# Deal out hands to players
		for i in range(len(hands)):
			self.players[i].dealHand(hands[i])

	def takeCall(self, playerNum):
		caller = self.players[playerNum]
		callee = self.players[self.currPlayer - 1]

		# Reveal cards
		cards = ', '.join([CARD_VALS[i] for i in self.lastAction])
		print "The cards are revealed to be: {}".format(cards)

		cardsTrue = [card == (self.currCard - 1) % 13 for card in self.lastAction]
		isHonest = reduce(lambda x, y: x and y, cardsTrue)
		# Add cards to player's hand if BS call is valid
		if not isHonest:
			for i in range(len(self.discard)):
				callee.hand[i] += self.discard[i]
			print "Player {} calls BS correctly! Player {}".format(playerNum, 
				   (self.currPlayer - 1) % self.numPlayers) + \
				  " adds the discard pile to his hand."
		# Add cards to caller's hand otherwise
		else:
			for i in range(len(self.discard)):
				caller.hand[i] += self.discard[i]
			print "Player {} calls BS incorrectly! He adds the discard".format(playerNum) + \
				  " pile to his hand."
		self.discard = [0 for _ in range(13)]

	def takeAction(self, action, playerNum):
		if len(action) == 1:
			print "\nPlayer {} puts down {} card".format(self.currPlayer, len(action))
		else:	
			print "\nPlayer {} puts down {} cards".format(self.currPlayer, len(action))
		player = self.players[playerNum]
		for card in action:
			player.hand[card] -= 1
			self.discard[card] += 1
		self.currCard = (self.currCard + 1) % 13
		self.currPlayer = (self.currPlayer + 1) % self.numPlayers
		self.lastAction = action

	def getActions(self, playerNum):
		player = self.players[playerNum]
		moves = []

		# Narrow down to valid moves
		for move in self.candidateMoves:
			handCopy = copy.copy(player.hand)
			isValid = True
			for card in move:
				handCopy[card] -= 1
				# print move, card, handCopy, handCopy[card]
				if handCopy[card] < 0:
					# print move, "It's invalid at {}".format(card)
					isValid = False
					# break
			if isValid:
				moves.append(move)

		# Remove repeats
		moves = [move for move in moves if sorted(move) == list(move)]
		#print moves
		return moves

	def printTurn(self):
		# Prints information for turn
		print "Player {}'s turn.".format(self.currPlayer)
		print "Discard deck size: {}".format(sum(self.discard))
		for i in range(len(self.players)):
			print "Player {}'s hand size: {}".format(i, sum(self.players[i].hand))
		print "Player must play: {}".format(CARD_VALS[self.currCard])

	def isOver(self):
		for player in self.players:
			if sum(player.hand) == 0:
				return True
		return False

	def winner(self):
		for i in range(len(self.players)):
			if sum(self.players[i].hand) == 0:
				return i
