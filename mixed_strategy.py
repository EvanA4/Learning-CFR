'''
For this program, ROCK, PAPER, and SCISSORS correspond to indices 0, 1, and 2, respectively.
Two strategy-adapting bots are going head to head to find the Nash equilibrium!
'''

import random


def getAction(strategy: list[float]) -> str:
    rand = random.random()
    if (rand < strategy[0]):
        return "ROCK"
    elif (rand < strategy[0] + strategy[1]):
        return "PAPER"
    else:
        return "SCISSORS"


def getPlayerStrategy(regretSum: list[str]) -> list[float]:
    # convert regretSum to strategy
    strategy = [
        regretSum[0] if regretSum[0] > 0 else 0,
        regretSum[1] if regretSum[1] > 0 else 0,
        regretSum[2] if regretSum[2] > 0 else 0
    ]

    # normalize strategy
    stratTotal = 0
    for probability in strategy:
        stratTotal += probability

    if stratTotal > 0:
        for i in range(3):
            strategy[i] /= stratTotal
    else:
        strategy = [1/3, 1/3, 1/3]
    
    return strategy


def getPlayerAction(regretSum: list[str], strategySum: list[str]) -> str:
    strategy = getPlayerStrategy(regretSum)

    # add strategy to strategySum
    for i in range(3):
        strategySum[i] += strategy[i]

    # determine player action with RNG
    return getAction(strategy)


def getUtilities(player_action: str, opponent_action: str) -> list[str]:
    ACTS_TO_UTILITY = {
        "ROCKPAPER": [-1, 1],
        "ROCKSCISSORS": [1, -1],
        "PAPERROCK": [1, -1],
        "PAPERSCISSORS": [-1, 1],
        "SCISSORSROCK": [-1, 1],
        "SCISSORSPAPER": [1, -1]
    }
    if (player_action == opponent_action):
        return [0, 0]
    else:
        return ACTS_TO_UTILITY[player_action + opponent_action]
    

def getRegrets(player_action: str, opponent_action: str) -> list[float]:
    ACTIONS = ["ROCK", "PAPER", "SCISSORS"]
    regrets = []

    for action in ACTIONS:
        regret = getUtilities(action, opponent_action)[0] - getUtilities(player_action, opponent_action)[0]
        regrets.append(regret)
    
    return regrets


def playRound(regretSum_p1: list[float], strategySum_p1: list[float], regretSum_p2: list[float], strategySum_p2: list[float]) -> None:
    # get both actions
    P1_ACTION = getPlayerAction(regretSum_p1, strategySum_p1)
    P2_ACTION = getPlayerAction(regretSum_p2, strategySum_p2)

    # compute regrets
    P1_REGRETS = getRegrets(P1_ACTION, P2_ACTION)
    P2_REGRETS = getRegrets(P2_ACTION, P1_ACTION)

    # add to regret sum
    for i in range(3):
        regretSum_p1[i] += P1_REGRETS[i]
        regretSum_p2[i] += P2_REGRETS[i]


def main():
    LOOPS = 50000
    regretSum_p1 = [0, 0, 0]
    strategySum_p1 = [0, 0, 0]
    regretSum_p2 = [0, 0, 0]
    strategySum_p2 = [0, 0, 0]

    # loop a bunch of times to converge to a strategy
    for i in range(LOOPS - 1):    
        playRound(regretSum_p1, strategySum_p1, regretSum_p2, strategySum_p2)

    print("Average strategy for player 1:")
    stratSumTotal_p1 = 0
    for probability in strategySum_p1:
        stratSumTotal_p1 += probability
    for i in range(3):
        strategySum_p1[i] /= stratSumTotal_p1
    print(strategySum_p1)

    print("Average strategy for player 2:")
    stratSumTotal_p2 = 0
    for probability in strategySum_p2:
        stratSumTotal_p2 += probability
    for i in range(3):
        strategySum_p2[i] /= stratSumTotal_p2
    print(strategySum_p1)



if __name__ == "__main__":
    main()