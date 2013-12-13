import agent, copy, evaluation, game, math, random, itertools

NUM_DECKS = 1
NUM_CARDS = 5 #Must be <= 13 and non-zero

def run_game(g, agents, verbose=1):
	# Welcome message
	if verbose != 0:
		print "\nWelcome to the card game BS! You are player 0, " + \
				  "and there are {} other players.".format(len(g.players)-1)
		print "==============================================================================="
		print "===============================================================================\n"
	
	# Initialize array of model based reflex agents
	modelReflexAgents = [a.playerNum for a in agents if isinstance(a, agent.ModelReflexAgent)]

	# Run game
	over = False
	currPlayer = 0
	totalAgentCalls = 0.0 #Debug
	totalPossibleCalls = 0.0 #Debug
	totalAgentRight = 0.0 #Debug
	while not over:
		# Print turn information
		if verbose != 0:
			g.printTurn()

		# Get actions for current player and select one to take
		currAgent = agents[currPlayer]
		moves = g.getActions(currPlayer)
		action = currAgent.getAction(moves, g)
		currPlayer = g.currPlayer
		g.takeAction(action, currPlayer, verbose)

		currCaller = g.currPlayer
		while(True):
			# Take the first call after the player who just played
			call = agents[currCaller].getCall(g, verbose)
			# Use call to update oppCallProbs for all model based reflex agents
			for a in modelReflexAgents:
				agents[a].updateCallProb(currCaller, call)
			if call:
				if currCaller == 0:        #Debug
					totalAgentCalls += 1   #Debug
				isLying = g.takeCall(currCaller, verbose)
				if isLying and currCaller == 0: #Debug
					totalAgentRight += 1 #Debug

				for a in modelReflexAgents:
					agents[a].updateLieProb(currPlayer, isLying)
				break
			currCaller = (currCaller + 1) % g.numPlayers

			# If we wrap around to the player who just played, break
			if currCaller == currPlayer:
				break
		
		totalPossibleCalls += 1            #Debug
		currPlayer = g.currPlayer
		over = g.isOver()
		if verbose != 0:
			print "\n=========================" + \
			      "======================================================\n"
	#print totalAgentCalls / totalPossibleCalls #Debug
	if totalAgentCalls != 0: #Debug
		print totalAgentRight / totalAgentCalls #Debug
	winner = g.winner()
	#print "The winner is player {}!".format(winner)
	return winner

def extractFeatures(state):
	game, playerNum = state
	features = []

	# Num cards in own hand
	features.append(sum(game.players[playerNum].hand))

	# Num cards in opponents hands
	for i in range(len(game.players)):
		if i != playerNum:
			features.append(sum(game.players[i].hand))
	
	# Size of discard pile
	features.append(sum(game.discard))

	# Number of i of a kind you have in your hand
	for i in range(0, 5):
		features.append(game.players[playerNum].hand.count(i))

	# Number of next two required cards you have
	
	# print "Current player: ", game.currPlayer
	# print "playerNum: ", playerNum
	# print "Current Card: ", game.currCard
	if game.currPlayer == playerNum:
		nextCard = (game.currCard + game.numPlayers) % NUM_CARDS
	else:
		nextCard = (game.currCard + (playerNum - game.currPlayer) % game.numPlayers) % NUM_CARDS
	nextNextCard = (nextCard + game.numPlayers) % NUM_CARDS
	# print "Next card: ", nextCard
	# print "Next next card: ", nextNextCard
	# print "\n"
	features.append(game.players[playerNum].hand[nextCard])
	features.append(game.players[playerNum].hand[nextNextCard])
	
	features+=game.players[playerNum].hand

	return features

def logLinearEvaluation(state, w):
    """
    Evaluate the current state using the log-linear evaluation
    function.

    @param state : Tuple of (game, playerNum), the game is
    a game object (see game.py for details, and playerNum
    is the number of the player for whose utility the state is
    being evaluated.

    @param w : List of feature weights.

    @returns V : Evaluation of current game state.
    """
    features = extractFeatures(state)
    dotProduct = sum([features[i] * w[i] for i in range(len(features))])
    V = float(1)/(1 + math.exp(-dotProduct))
    return V

def TDUpdate(state, nextState, reward, w, eta):
    """
    Given two sequential game states, updates the weights
    with a step size of eta, using the Temporal Difference learning
    algorithm.

    @param state : Tuple of game state (game object, player).
    @param nextState : Tuple of game state (game object, player),
    note if the game is over this will be None. In this case, 
    the next value for the TD update will be 0.
    @param reward : The reward is 1 if the game is over and your
    player won, 0 otherwise.
    @param w : List of feature weights.
    @param eta : Step size for learning.

    @returns w : Updated weights.
    """
    if nextState:
        residual = reward + logLinearEvaluation(nextState, w) - logLinearEvaluation(state, w)
    else: 
        residual = reward - logLinearEvaluation(state, w)
    phi = extractFeatures(state)
    expTerm = math.exp(-sum([phi[i] * w[i] for i in range(len(phi))]))
    gradCoeff = expTerm / math.pow((1 + expTerm), 2)
    for i in range(len(w)):
        gradient = phi[i] * gradCoeff
        w[i] += (eta * residual * gradient)
    return w

def train(numAgents=3, numGames=30):
	alpha = 1e-1
	numFeats = 8 + numAgents + NUM_CARDS #Debug 
	
	weightVector = []
	for i in range(numAgents):
		weight = [random.gauss(-1e-1, 1e-2) for _ in range(numFeats)]
		weightVector.append(weight)
	
	#agents = [agent.ReflexAgent(i, logLinearEvaluation, weightVector[i]) for i in range(numAgents)]
	agents = [agent.ModelReflexAgent(i, numAgents, logLinearEvaluation, weightVector[i]) for i in range(numAgents)]
	# Initialize array of model based reflex agents
	modelReflexAgents = [a.playerNum for a in agents if isinstance(a, agent.ModelReflexAgent)]

	#Single weight vector
	#w = [random.gauss(1e-3, 1e-1) for _ in range(numFeats)]
	#agents = [agent.ReflexAgent(i, logLinearEvaluation, w) for i in range(numAgents)]

	# agents = [agent.ReflexAgent(0, logLinearEvaluation, w)]
	# for i in range(1, numAgents):
	# 	agents.append(agent.ReflexAgent(i, evaluation.simpleEvaluation))

	i = 0
	winners = [0 for i in range(numAgents)]
	while i < numGames:
		#print i
		g = game.Game(len(agents), NUM_DECKS)

		# Run game
		over = False
		currPlayer = 0

		cycle = False
		turnCounter = 0
		threshold = 100
		oldW = list(weightVector[currPlayer])
		oldAgents = copy.deepcopy(agents)

		while not over:
			if turnCounter > threshold:
				cycle = True
				break
			turnCounter += 1
			#print turnCounter

			states = [(g.clone(), currPlayer)]

			# Get actions for current player and select one to take
			currAgent = agents[currPlayer]
			moves = g.getActions(currPlayer)
			action = currAgent.getAction(moves, g)
			# if currPlayer == 0:
			# 		print "========================================="
			# print "Required card: ", g.currCard
			currPlayer = g.currPlayer
			g.takeAction(action, currPlayer, verbose=0)
			# print "Hands: ", g.players[0].hand, g.players[1].hand, g.players[2].hand

			currCaller = g.currPlayer
			
			while(True):
				# Take the first call after the player who just played
				call = agents[currCaller].getCall(g, verbose=0)
				for a in modelReflexAgents:
					agents[a].updateCallProb(currCaller, call)
				#states.append((g.clone(), currCaller))
				if call:
					isLying = g.takeCall(currCaller, verbose=0)
					for a in modelReflexAgents:
						agents[a].updateLieProb(currPlayer, isLying)
					break
				currCaller = (currCaller + 1) % g.numPlayers

				# If we wrap around to the player who just played, break
				if currCaller == currPlayer:
					break

			for state in states:
				nextState = (g, state[1])
				weightVector[currPlayer] = TDUpdate(state,nextState,0, weightVector[currPlayer],alpha)

			agents[currPlayer].setWeights(weightVector[currPlayer])

			currPlayer = g.currPlayer
			over = g.isOver()

		if not cycle:
			winner = g.winner()
			weightVector[winner] = TDUpdate((g, winner),None, 1.0, weightVector[winner] ,alpha)
			i += 1
			#print "Noncycle"
			winners[winner] += 1
		else:
			w = oldW
			agents = oldAgents
		#print "The winner is player {}!".format(winner)

	#print weightVector #Debug
	#print winners.index(max(winners))	
	
	#Get weight vector that won the most
	index = winners.index(max(winners))
	return weightVector[index]

def test(agents, numGames=10):
	playerWin = [0 for i in range(len(agents))] #Our agent won, other agent won
	for i in range(numGames):
		#print "On game: " + str(i + 1)
		g = game.Game(len(agents), NUM_DECKS)
		winner = run_game(g, agents, verbose=0) #Debug
		playerWin[winner] += 1
	for j in range(len(agents)):
		if j == 0: #Debug
			#print "Player {} win rate: {}".format(j, float(playerWin[j]) / sum(playerWin)) #Debug
	 		print float(playerWin[j]) / sum(playerWin)

def main(args=None):
	
	# arr = [agent.HumanAgent(0)]
	# arr = [agent.ReflexAgent(0, evaluation.simpleEvaluation)]
	# for i in range(1, NUM_COMPUTERS+1):
	# 	arr.append(agent.RandomAgent(i))
	# g = game.Game(len(arr), NUM_DECKS)

	numPlayers = 4
	numIters = 100
	numTrials = 100
	numRuns = 10

	# print "Reflex agent against random agents"
	# arr = [agent.ReflexAgent(0, logLinearEvaluation, w)]
	# for i in range(1, numPlayers):
	#        arr.append(agent.RandomAgent(i))
	# g = game.Game(numPlayers, NUM_DECKS)
	# test(arr, numTrials)

	# print "Reflex agent against simple evaluation agents"
	# arr = [agent.ReflexAgent(0, logLinearEvaluation, w)]
	# for i in range(1, numPlayers):
	#        arr.append(agent.ReflexAgent(i, evaluation.simpleEvaluation))
	# g = game.Game(numPlayers, NUM_DECKS)
	# test(arr, numTrials)

	# print "Reflex agent against honest agents"
	# arr = [agent.ReflexAgent(0, logLinearEvaluation, w)]
	# for i in range(1, numPlayers):
	#        arr.append(agent.HonestAgent(i))
	# g = game.Game(numPlayers, NUM_DECKS)
	# test(arr, numTrials)

	# print "Reflex agent against dishonest agents"
	# arr = [agent.ReflexAgent(0, logLinearEvaluation, w)]
	# for i in range(1, numPlayers):
	#        arr.append(agent.DishonestAgent(i))
	# g = game.Game(numPlayers, NUM_DECKS)
	# test(arr, numTrials)

	# print "Reflex agent against AlwaysCallBSAgent"
	# arr = [agent.ReflexAgent(0, logLinearEvaluation, w)]
	# for i in range(1, numPlayers):
	#       arr.append(agent.AlwaysCallBSAgent(i))
	# g = game.Game(numPlayers, NUM_DECKS)
	# test(arr, numTrials)

	for i in range(numRuns):
		print "TRIAL", i
		#print "Training on {} players for {} iterations...".format(numPlayers, numIters)
		w = train(numPlayers, numIters)

		#print "Model based reflex agent against random agents"
		arr = [agent.ModelReflexAgent(0, numPlayers, logLinearEvaluation, w)]
		for i in range(1, numPlayers):
			arr.append(agent.RandomAgent(i))
		g = game.Game(numPlayers, NUM_DECKS)
		test(arr, numTrials)

		#print "Model based reflex agent against simple evaluation agents"
		arr = [agent.ModelReflexAgent(0, numPlayers, logLinearEvaluation, w)]
		for i in range(1, numPlayers):
		       arr.append(agent.ReflexAgent(i, evaluation.simpleEvaluation))
		g = game.Game(numPlayers, NUM_DECKS)
		test(arr, numTrials)

		#print "Model based reflex agent against honest agents"
		arr = [agent.ModelReflexAgent(0, numPlayers, logLinearEvaluation, w)]
		for i in range(1, numPlayers):
		       arr.append(agent.HonestAgent(i))
		g = game.Game(numPlayers, NUM_DECKS)
		test(arr, numTrials)

		#print "Model based reflex agent against dishonest agents"
		arr = [agent.ModelReflexAgent(0, numPlayers, logLinearEvaluation, w)]
		for i in range(1, numPlayers):
		       arr.append(agent.DishonestAgent(i))
		g = game.Game(numPlayers, NUM_DECKS)
		test(arr, numTrials)

		#print "Model based reflex agent against AlwaysCallBSAgent"
		arr = [agent.ModelReflexAgent(0, numPlayers, logLinearEvaluation, w)]
		for i in range(1, numPlayers):
		      arr.append(agent.AlwaysCallBSAgent(i))
		g = game.Game(numPlayers, NUM_DECKS)
		test(arr, numTrials)

	# # #print "Simple evaluation against random agents"
	# arr = [agent.ReflexAgent(0, evaluation.simpleEvaluation)]
	# for i in range(1, numPlayers):
	#        arr.append(agent.RandomAgent(i))
	# g = game.Game(numPlayers, NUM_DECKS)
	# test(arr, numTrials)

	# #print "Simple agent against simple evaluation agents"
	# arr = [agent.ReflexAgent(0, evaluation.simpleEvaluation)]
	# for i in range(1, numPlayers):
	#        arr.append(agent.ReflexAgent(i, evaluation.simpleEvaluation))
	# g = game.Game(numPlayers, NUM_DECKS)
	# test(arr, numTrials)

	# #print "Simple agent against honest agents"
	# arr = [agent.ReflexAgent(0, evaluation.simpleEvaluation)]
	# for i in range(1, numPlayers):
	#        arr.append(agent.HonestAgent(i))
	# g = game.Game(numPlayers, NUM_DECKS)
	# test(arr, numTrials)

	# #print "Simple agent against dishonest agents"
	# arr = [agent.ReflexAgent(0, evaluation.simpleEvaluation)]
	# for i in range(1, numPlayers):
	#        arr.append(agent.DishonestAgent(i))
	# g = game.Game(numPlayers, NUM_DECKS)
	# test(arr, numTrials)

	# #print "Simple agent against AlwaysCallBSAgent"
	# arr = [agent.ReflexAgent(0, evaluation.simpleEvaluation)]
	# for i in range(1, numPlayers):
	#       arr.append(agent.AlwaysCallBSAgent(i))
	# g = game.Game(numPlayers, NUM_DECKS)
	# test(arr, numTrials)

	#while True:
	#	g = game.Game(numPlayers, NUM_DECKS)
	#	run_game(g, [agent.HumanAgent(0), agent.ReflexAgent(1, logLinearEvaluation, w), agent.ReflexAgent(2, logLinearEvaluation, w)])

if __name__=="__main__":
    main()
