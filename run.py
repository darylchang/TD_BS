import agent, game, random

def run_game(g, agents):
	# Welcome message
	print "\nWelcome to the card game BS! You are player 0, " + \
			  "and there are {} other players.".format(len(g.players)-1)
	print "==============================================================================="
	print "===============================================================================\n"
	
	# Run game
	over = False
	currPlayer = 0
	while not over:
		# Print turn information
		g.printTurn()

		# Get actions for current player and select one to take
		currAgent = agents[currPlayer]
		moves = g.getActions(currPlayer)
		action = currAgent.getAction(moves, g)
		g.takeAction(action, currPlayer)
		currPlayer = g.currPlayer

		# Check if anyone wants to call BS. If so, randomly select one to do so.
		callers = []
		for i in range(len(agents)):
			if agents[i].getCall(g):
				callers.append(i)
		if callers:
			caller = random.choice(callers)
			g.takeCall(caller)

		over = g.isOver()
		print "\n"

	winner = g.winner()
	print "The winner is player {}!".format(winner)

def main(args=None):
	g = game.Game()
	p1 = agent.HumanAgent(0)
	p2 = agent.RandomAgent(1)
	p3 = agent.RandomAgent(2)
	run_game(g, [p1, p2, p3])

if __name__=="__main__":
    main()