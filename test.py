import agent, evaluation, game, run

def testSimpleEvaluation():
	g = game.Game(numPlayers=3, numDecks=1)
	print g.players[0].hand
	print g.players[1].hand
	print g.players[2].hand
	for i in range(g.numPlayers):
		print "Eval score for player {}: {}".format(i, evaluation.simpleEvaluation((g, i)))

def testExtractFeatures():
	g = game.Game(numPlayers=3, numDecks=1)
	print g.players[0].hand
	print g.players[1].hand
	print g.players[2].hand
	print "\n"
	print run.extractFeatures((g, 0))
	print run.extractFeatures((g, 1))
	print run.extractFeatures((g, 2))

testSimpleEvaluation()
testExtractFeatures()