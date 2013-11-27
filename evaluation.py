"""
Simple evaluation function that returns the score for 
a given state (a tuple of (game, playerNum)).  The score
is calculated as the avg number of cards in opponents' hands
minus the number of cards in the agent's hand.
"""
def simpleEvaluation(state):
	g, playerNum = state
	V = -sum(g.players[playerNum].hand)
	numOppCards = sum([sum(player.hand) for player in g.players if player.number != playerNum])
	avgOppCards = numOppCards / float(g.numPlayers - 1)
	V += avgOppCards
	return V
