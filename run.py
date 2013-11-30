import agent, evaluation, game, random, itertools

def run_game(g, agents, verbose=1):
	# Welcome message
	if verbose != 0:
		print "\nWelcome to the card game BS! You are player 0, " + \
				  "and there are {} other players.".format(len(g.players)-1)
		print "==============================================================================="
		print "===============================================================================\n"
	
	# Run game
	over = False
	currPlayer = 0
	while not over:
		# Print turn information
		if verbose != 0:
			g.printTurn()

		# Get actions for current player and select one to take
		currAgent = agents[currPlayer]
		moves = g.getActions(currPlayer)
		action = currAgent.getAction(moves, g)
		g.takeAction(action, currPlayer, verbose)
		currPlayer = g.currPlayer

		currCaller = g.currPlayer
		while(True):
			# Take the first call after the player who just played
			call = agents[currCaller].getCall(g, verbose)
			if call:
				g.takeCall(currCaller, verbose)
				break
			currCaller = (currCaller + 1) % g.numPlayers

			# If we wrap around to the player who just played, break
			if currCaller == (g.currPlayer - 1) % g.numPlayers:
				break
	
		over = g.isOver()
		if verbose != 0:
			print "\n=========================" + \
			      "======================================================\n"

	winner = g.winner()
	print "The winner is player {}!".format(winner)
	return winner

NUM_DECKS = 1
NUM_COMPUTERS = 2

def test(players, numGames=10):
	playerWin = [0 for i in range(len(players))] #Our agent won, other agent won
	for i in range(numGames):
		print "On game: " + str(i + 1)
		g = game.Game(len(players), NUM_DECKS)
		winner = run_game(g, players, verbose=0)
		playerWin[winner] += 1
	for j in range(len(players)):
		print "Player {} win rate: {}".format(j, float(playerWin[j]) / sum(playerWin))
	

def main(args=None):
	
	# arr = [agent.HumanAgent(0)]
	arr = [agent.ReflexAgent(0, evaluation.simpleEvaluation)]
	for i in range(1, NUM_COMPUTERS+1):
		arr.append(agent.RandomAgent(i))
	g = game.Game(len(arr), NUM_DECKS)
	test(arr, 10)
	# run_game(g, arr)

if __name__=="__main__":
    main()