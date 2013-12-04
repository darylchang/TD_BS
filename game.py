from player import Player
import copy, itertools, random, run

CARD_VALS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

# Create all possible moves
candidateMoves = []
cards = [i for i in range(run.NUM_CARDS)]
for i in range(1, 5):
	candidateMoves += list(itertools.product(cards, repeat=i))

class Game:

	def __init__(self, numPlayers=3, numDecks=1, 
				 players=None, currPlayer=None, currCard=None, lastAction=None,
				 discard=None):
		self.candidateMoves = candidateMoves
		self.players = copy.deepcopy(players) if players else [Player(i) for i in range(numPlayers)]
		self.numPlayers = numPlayers
		self.numDecks = numDecks
		self.currPlayer = currPlayer if currPlayer else 0
		self.currCard = currCard if currCard else 0
		self.lastAction = lastAction if lastAction else []
		self.discard = copy.deepcopy(discard) if discard else [0 for _ in range(run.NUM_CARDS)]
		if not players:
			self.dealCards()
		
	def dealCards(self):
		# Create deck of cards
		deck = []
		for i in range(4 * self.numDecks):
			for j in range(run.NUM_CARDS):
				deck.append(j)
		random.shuffle(deck)
		
		# Separate into hands
		handSize = len(deck) / len(self.players)
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

	def takeCall(self, playerNum, verbose=False):
		caller = self.players[playerNum]
		callee = self.players[(self.currPlayer - 1) % self.numPlayers]

		# Reveal cards
		cards = ', '.join([CARD_VALS[i] for i in self.lastAction])
		if verbose:
			print "BS was called by Player {}. The cards are revealed to be: {}".format(playerNum, cards)

		cardsTrue = [card == (self.currCard - 1) % run.NUM_CARDS for card in self.lastAction]
		isHonest = reduce(lambda x, y: x and y, cardsTrue)
		# Add cards to player's hand if BS call is valid
		if not isHonest:
			self.addDiscard(callee.number)
			if verbose:
				print "Player {} calls BS correctly! Player {}".format(playerNum, 
				   	   (self.currPlayer - 1) % self.numPlayers) + \
				  	  " adds the discard pile to his hand."
		# Add cards to caller's hand otherwise
		else:
			self.addDiscard(caller.number)
			if verbose:
				print "Player {} calls BS incorrectly! He adds the discard".format(playerNum) + \
					  " pile to his hand."

	def addDiscard(self, playerNum):
		for i in range(len(self.discard)):
			self.players[playerNum].hand[i] += self.discard[i]
		self.discard = [0 for _ in range(run.NUM_CARDS)]

	def takeAction(self, action, playerNum, verbose=False):
		if verbose:
			if len(action) == 1:
				print "\nPlayer {} puts down {} card".format(self.currPlayer, len(action))
			else:	
				print "\nPlayer {} puts down {} cards".format(self.currPlayer, len(action))
		player = self.players[playerNum]
		for card in action:
			player.hand[card] -= 1
			self.discard[card] += 1
		self.currCard = (self.currCard + 1) % run.NUM_CARDS
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

	def clone(self):
		return Game(self.numPlayers, self.numDecks, 
				 self.players, self.currPlayer, self.currCard, self.lastAction,
				 self.discard)