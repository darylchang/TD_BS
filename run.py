import agent, copy, evaluation, game, math, random, itertools, argparse

NUM_DECKS = 1
NUM_CARDS = 5 # Must be <= 13 and non-zero

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
				isLying = g.takeCall(currCaller, verbose)
				for a in modelReflexAgents:
					agents[a].updateLieProb(currPlayer, isLying)
				break
			currCaller = (currCaller + 1) % g.numPlayers

			# If we wrap around to the player who just played, break
			if currCaller == currPlayer:
				break
		
		currPlayer = g.currPlayer
		over = g.isOver()
		if verbose != 0:
			print "\n=========================" + \
			      "======================================================\n"
	winner = g.winner()
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
	if game.currPlayer == playerNum:
		nextCard = (game.currCard + game.numPlayers) % NUM_CARDS
	else:
		nextCard = (game.currCard + (playerNum - game.currPlayer) % game.numPlayers) % NUM_CARDS
	nextNextCard = (nextCard + game.numPlayers) % NUM_CARDS
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

"""
Plays a training tournament between the reflex or model agents and picks 
the one that won its round to advance.  At the end, return the weight
vector of the overall winner.
"""
def tournament(numPlayers=3, numIters=50, numContenders = 27, isModel=False):
	tournamentArr = []
	for i in range(numContenders):
		tournamentArr.append(train(numPlayers, numIters))
	
	while(len(tournamentArr) != 1):
		newArr = []
		iterable = iter(tournamentArr)
		for i in iterable:
			weights = [i, iterable.next(), iterable.next()]
			w = train(numPlayers, numIters, isModel, weights)
			newArr.append(w)
		tournamentArr = newArr
	
	return tournamentArr[0]


"""
Trains reflex or model agents using TD learning. Returns the resulting 
weight vector.
"""
def train(numAgents=3, numGames=50, isModel=False, weights = None): 
	print "Training on {} players for {} iterations...".format(numAgents, numGames)
	alpha = 1e-1
	numFeats = 8 + numAgents + NUM_CARDS 
	
	weightVector = []
	for i in range(numAgents):
		weight = [random.gauss(-1e-1, 1e-2) for _ in range(numFeats)]
		weightVector.append(weight)
	
	if not weights:
		if isModel:
			agents = [agent.ModelReflexAgent(i, numAgents, logLinearEvaluation, weightVector[i]) for i in range(numAgents)]
		else:
			agents = [agent.ReflexAgent(i, logLinearEvaluation, weightVector[i]) for i in range(numAgents)]
	else:
		agents = []
		for i in range(len(weights)):
			if isModel:
				agents.append(agent.ModelReflexAgent(i, numAgents, logLinearEvaluation, weights[i]))
			else:
				agents.append(agent.ReflexAgent(i, logLinearEvaluation, weights[i]))

	# Initialize array of model based reflex agents
	modelReflexAgents = [a.playerNum for a in agents if isinstance(a, agent.ModelReflexAgent)]

	i = 0
	winners = [0 for i in range(numAgents)]
	while i < numGames:
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

			states = [(g.clone(), currPlayer)]

			# Get actions for current player and select one to take
			currAgent = agents[currPlayer]
			moves = g.getActions(currPlayer)
			action = currAgent.getAction(moves, g)
			currPlayer = g.currPlayer
			g.takeAction(action, currPlayer, verbose=0)

			currCaller = g.currPlayer
			
			while(True):
				# Take the first call after the player who just played
				call = agents[currCaller].getCall(g, verbose=0)
				for a in modelReflexAgents:
					agents[a].updateCallProb(currCaller, call)
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
			winners[winner] += 1
		else:
			i += 1
			w = oldW
			agents = oldAgents
	
	#Get weight vector that won the most
	index = winners.index(max(winners))
	return weightVector[index]

def test(agents, numGames=100, verbose=0):
	playerWin = [0 for i in range(len(agents))] #Our agent won, other agent won
	for i in range(numGames):
		g = game.Game(len(agents), NUM_DECKS)
		winner = run_game(g, agents, verbose)
		playerWin[winner] += 1
	for j in range(len(agents)):
		if j == 0:
			winRate = float(playerWin[j]) / sum(playerWin)
			print "Player {} win rate: {}".format(j, winRate)
	return winRate

def main(args=None):
	# Parse command line arguments
	argNames = ['-trainGames', '-run', '-p', '-test', '-agent', '-opp', '-tournament', '-human', '-verbose']
	parser = argparse.ArgumentParser(description='Process input parameters.')
	for arg in argNames:
		parser.add_argument(arg)
	namespace = parser.parse_args()
	
	numPlayers = getattr(namespace, 'p') if getattr(namespace, 'p') else 3
	numTrainGames = getattr(namespace, 'trainGames')if getattr(namespace, 'trainGames') else 50
	numTestGames = getattr(namespace, 'test') if getattr(namespace, 'test') else 100
	numRuns = getattr(namespace, 'run') if getattr(namespace, 'run') else 10
	agentType = getattr(namespace, 'agent') if getattr(namespace, 'agent') else 'model'
	oppType = getattr(namespace, 'opp') if getattr(namespace, 'opp') else 'simple'
	isTournament = (getattr(namespace, 'tournament') == 'y')
	isHuman = (getattr(namespace, 'human') == 'y')
	verbose = (getattr(namespace, 'verbose') == 'y')

	winRates = []
	for i in range(numRuns):

		# Play a game with human agent
		if isHuman:
			agents = [agent.HumanAgent(0)]
			for j in range(1, numPlayers):
				if oppType == 'random':
					agents.append(agent.RandomAgent(j))
				elif oppType == 'simple':
					agents.append(agent.ReflexAgent(j, evaluation.simpleEvaluation))
				elif oppType == 'honest':
					agents.append(agent.HonestAgent(j))
				elif oppType == 'dishonest':
					agents.append(agent.DishonestAgent(j))
				elif oppType == 'bs':
					agents.append(agent.AlwaysCallBSAgent(j))
			g = game.Game(numPlayers, NUM_DECKS)
			run_game(g, agents)

		# Play a game with computer agent
		else:
			agents = []
			if agentType == 'random':
				agents.append(agent.RandomAgent(0))
			elif agentType == 'simple':
				agents.append(agent.ReflexAgent(0, evaluation.simpleEvaluation))
			elif agentType == 'honest':
				agents.append(agent.HonestAgent(0))
			elif agentType == 'dishonest':
				agents.append(agent.DishonestAgent(0))
			elif agentType == 'bs':
				agents.append(agent.AlwaysCallBSAgent(0))
			elif agentType == 'reflex':
				if isTournament:
					w = tournament(numPlayers, numTrainGames)
					a = agent.ReflexAgent(0, logLinearEvaluation, w)
					agents.append(a)
				else:
					w = train(numPlayers, numTrainGames)
					a = agent.ReflexAgent(0, logLinearEvaluation, w)
					agents.append(a)
			elif agentType == 'model':
				if isTournament:
					w = tournament(numPlayers, numTrainGames, isModel=True)
					a = agent.ModelReflexAgent(0, numPlayers, logLinearEvaluation, w)
					agents.append(a)
				else:
					w = train(numPlayers, numTrainGames, isModel=True)
					a = agent.ModelReflexAgent(0, numPlayers, logLinearEvaluation, w)
					agents.append(a)

			for j in range(1, numPlayers):
				if oppType == 'random':
					agents.append(agent.RandomAgent(j))
				elif oppType == 'simple':
					agents.append(agent.ReflexAgent(j, evaluation.simpleEvaluation))
				elif oppType == 'honest':
					agents.append(agent.HonestAgent(j))
				elif oppType == 'dishonest':
					agents.append(agent.DishonestAgent(j))
				elif oppType == 'bs':
					agents.append(agent.AlwaysCallBSAgent(j))

			winRates.append(test(agents, numTestGames, verbose))

	if winRates:
		avgWinRate = sum(winRates) / numRuns
		print "Average win rate of agent is: {}".format(avgWinRate)

if __name__=="__main__":
    main()
