import agent, evaluation, game

def testSimpleEvaluation():
	g = game.Game(numPlayers=3, numDecks=1)
	print g.players[0].hand
	print g.players[1].hand
	print g.players[2].hand
	for i in range(g.numPlayers):
		print "Eval score for player {}: {}".format(i, evaluation.simpleEvaluation((g, i)))

testSimpleEvaluation()