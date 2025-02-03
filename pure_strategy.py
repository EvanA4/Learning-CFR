'''
For this program, ROCK, PAPER, and SCISSORS correspond to indices 0, 1, and 2, respectively.
One strategy-adapting bot will find the best strategy against a mixed-strategy opponent.
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


def getOpponentAction() -> str:
    STRATEGY = [.6, .2, .2] # <----------- Tweak the opponent's strategy and see its effects!
    return getAction(STRATEGY)


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


def playRound(regretSum: list[float], strategySum: list[float]) -> None:
    # get both actions
    PLAYER_ACTION = getPlayerAction(regretSum, strategySum)
    OPPONENT_ACTION = getOpponentAction()

    # compute regrets
    REGRETS = getRegrets(PLAYER_ACTION, OPPONENT_ACTION)

    # add to regret sum
    for i in range(3):
        regretSum[i] += REGRETS[i]


def main():
    LOOPS = 50000
    regretSum = [0, 0, 0]
    strategySum = [0, 0, 0]

    # loop a bunch of times to converge to a strategy
    for i in range(LOOPS - 1):    
        playRound(regretSum, strategySum)

    print("Average strategy:")
    stratSumTotal = 0
    for probability in strategySum:
        stratSumTotal += probability
    for i in range(3):
        strategySum[i] /= stratSumTotal

    print(strategySum)


if __name__ == "__main__":
    main()