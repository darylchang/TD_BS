from player import Player
import copy, itertools, random

class Game:

	def __init__(self, numPlayers=3, numDecks=1):
		self.players = [Player(i) for i in range(numPlayers)]
		self.numPlayers = numPlayers
		self.numDecks = numDecks
		self.dealCards()

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

	def takeAction(self, action, playerNum):
		print "Hello"

	def getActions(self, playerNum):
		player = self.players[playerNum]
		cards = [i for i in range(13)]
		candidateMoves = []
		moves = []

		# Create all possible moves
		for i in range(1, 5):
			candidateMoves.append(list(itertools.product(cards, repeat=i)))

		# Narrow down to valid moves
		for move in candidateMoves:
			handCopy = copy.copy(player.hand)
			isValid = True
			for card in move:
				handCopy[card] -= 1
				if handCopy[card] < 0:
					isValid = False
					break
			if isValid:
				moves.append(move)

		print moves
		
		for move in moves:
			handCopy = copy.copy(player.hand)
			for card in cards:
				handCopy[card] -= 1

					




