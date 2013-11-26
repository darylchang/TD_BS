import copy, random

class Player:

	def __init__(self, number, isHuman=False):
		self.number = number
		self.isHuman = isHuman
		self.hand = [0 for i in range(13)]

	def dealHand(self,arr):
		for i in arr:
			self.hand[i] += 1

class GameEngine:

	def __init__(self, numHumans, numComputers, numDecks=1):
		self.numHumans = numHumans
		self.numComputers = numComputers
		self.numDecks = numDecks
		self.players = [Player(i, isHuman=True) for i in range(numHumans)]
		self.players += [Player(i + numHumans) for i in range(numComputers)]

	def dealCards(self):
		deck = []
		for i in range(4 * self.numDecks):
			for j in range(13):
				deck.append(j)
		random.shuffle(deck)
		
		handSize = 52 / len(self.players)
		hands = []
		for i in range(len(self.players)):
			if i != len(self.players) - 1:
				hand = deck[i * handSize : (i+1) * handSize]
			else: 
				hand = deck[i * handSize: 52]
			hands.append(hand)
		random.shuffle(hands)

		for i in range(len(hands)):
			self.players[i].dealHand(hands[i])
	
	def play(self):
		self.dealCards()
		self.cardVals = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
		currVal = 0
		currPlayer = 0
		discardDeck = [0 for i in range(13)]
		
		print "\nWelcome to the card game BS! You are player 1, " + \
			  "and there are {} other players.".format(len(self.players)-1)
		print "==============================================================================="
		print "===============================================================================\n"
		while(True):
			print "Player {}'s turn.".format(currPlayer + 1)
			print "Discard deck size: {}".format(sum(discardDeck))
			for i in range(len(self.players)):
				if i != currPlayer:
					print "Player {}'s hand size: {}".format(i + 1, sum(self.players[i].hand))
			if currPlayer == 0:
				self.playHuman(currVal, discardDeck)
				self.checkBSCall(currPlayer, currVal, discardDeck)
				
		
			else:
				self.playHuman(currVal, discardDeck)
			
			if sum(self.players[currPlayer].hand) == 0:
				print "Player {} Wins!!!\n".format(currPlayer)
				break
				
			#Increment current value and player	
			currVal+=1
			currPlayer+=1
			if currVal > 12: currVal = 0
			if currPlayer > len(self.players) - 1: currPlayer = 0


	def playHuman(self, currVal, discardDeck):
		formattedHand = []
		for i in range(13):
			for j in range(self.players[0].hand[i]):
				formattedHand.append(self.cardVals[i])
		print "Your hand: {}".format(formattedHand)
		print "\nMust play {}\n".format(self.cardVals[currVal])

		while(True):
			isValid = True
			newFormattedHand = copy.copy(formattedHand)
			cardsPlayed = raw_input("Which cards do you want to play? " + \
									"Enter a space-separated list of up to 4 cards: ")
			cardsPlayed = cardsPlayed.split()
			if len(cardsPlayed) > 4 or len(cardsPlayed) < 1:
				print "Please enter a valid number of cards."
				isValid = False
				continue
			for card in cardsPlayed:
				if card in newFormattedHand:
					newFormattedHand.remove(card)
				else:
					print "Please enter cards you have in your hand."
					isValid = False
					break
			if isValid:
				break
				
		for card in cardsPlayed:
			index = self.cardVals.index(card)
			discardDeck[index] += 1
			self.players[0].hand[index] -= 1
	
	def checkBSCall(self, currPlayer, currVal, discardDeck):
		print "\nNo players called BS!\n"
		print "===============================================================================\n"
		
			


game = GameEngine(1, 2)
game.play()




