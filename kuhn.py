from tabulate import tabulate

# Define global constants
ITERATIONS = 1

CARDS = [
    "K", "Q", "J"
]

ACTIONS = [
    "b", "p"
]

TERMINAL_ACTION_SET = {
    "pp", "bb", "pbp", "pbb"
}

INFOSET_STRS = [
    "K", "Q", "J",
    "Kb", "Kp",
    "Qb", "Qp",
    "Jb", "Jp",
    "Kpb", "Qpb", "Jpb"
]

# Define infoSets map
infoSets: dict[str, type['InfoSet']] = {}
cumulativeGains = 0


# Helper functions
def getGameUtility(pocket1: str, pocket2: str, isBet: bool):
    return (CARDS.index(pocket1) < CARDS.index(pocket2)) * (1 + isBet)


class InfoSet():
    def __init__(self, setStr: str) -> None:
        self.setStr = setStr
        self.gainsSum = [0, 0]
        self.strategy = [0, 0]
        self.beliefs = [0, 0]
        self.utils = [0, 0]
        self.utility = 0
        self.reach = 0

    def getParents(self) -> list[str]:
        if len(self.setStr) == 1:
            return []

        parents = []
        SUBSTR = self.setStr[1 : -1]
        for CARD in CARDS:
            if CARD != self.setStr[0]:
                parents.append(CARD + SUBSTR)

        return parents
    
    def setStrategies(self) -> None:
        total = self.gainsSum[0] + self.gainsSum[1]
        if total:
            self.strategy[0] = self.gainsSum[0] / total
            self.strategy[1] = self.gainsSum[1] / total
        else:
            self.strategy[0] = 1/2
            self.strategy[1] = 1/2
    
    def setBeliefs(self) -> None:
        # split computation based on depth of node
        if len(self.setStr) == 1:
            self.beliefs = [.5, .5]
        
        # just take normalization of parent's strategies
        else:
            PARENTS = self.getParents()
            ACTION_IDX = ACTIONS.index(self.setStr[-1])
            PROBS = [
                infoSets[PARENTS[0]].strategy[ACTION_IDX],
                infoSets[PARENTS[1]].strategy[ACTION_IDX]
            ]
            TOTAL = PROBS[0] + PROBS[1]
            if TOTAL:
                self.beliefs[0] = PROBS[0] / TOTAL
                self.beliefs[1] = PROBS[1] / TOTAL
            else:
                self.beliefs[0] = .5
                self.beliefs[1] = .5

    def setUtils(self) -> None:
        for ACTION in ACTIONS:
            # check if terminating
            actionStr = self.setStr[1:-1] + ACTION
            if actionStr in TERMINAL_ACTION_SET:
                parents = self.getParents()

                # add utility of both possible outcomes
                # -- if both bet
                if actionStr[-1] == "b":
                    self.utils[ACTIONS.index(ACTION)] = self.beliefs[0] * getGameUtility(self.setStr[0], parents[0][0], True)
                    self.utils[ACTIONS.index(ACTION)] += self.beliefs[1] * getGameUtility(self.setStr[0], parents[1][0], True)
                # -- if both pass
                elif actionStr.find("pp") != -1:
                    self.utils[ACTIONS.index(ACTION)] = self.beliefs[0] * getGameUtility(self.setStr[0], parents[0][0], False)
                    self.utils[ACTIONS.index(ACTION)] += self.beliefs[1] * getGameUtility(self.setStr[0], parents[1][0], False)
                # -- if one passes after the other bets
                else:
                    self.utils[ACTIONS.index(ACTION)] = -1
            
            # check if second player is playing bet after player 1 played pass
            elif len(self.setStr) == 2:
                self.utils[0] = 0
                ctr = 0
                for CARD in CARDS:
                    if CARD != self.setStr[0]:
                        child = infoSets[CARD + actionStr]
                        # if player 1 bets
                        self.utils[0] += self.beliefs[ctr] * (child.strategy[0] * getGameUtility(self.setStr[0], CARD, True))
                        # if player 1 passes
                        self.utils[0] += self.beliefs[ctr] * (child.strategy[1] * 1)
                        ctr += 0

            # calculate utilities for the root node's corresponding action :(
            else:
                # if played bet, get expected utility of player 2's actions
                if ACTION == "b":
                    self.utils[0] = 0
                    for CARD in CARDS:
                        if CARD != self.setStr[0]:
                            child = infoSets[CARD + actionStr]
                            # player 2 could play either bet or pass
                            self.utils[0] += .5 * (
                                child.strategy[0] * getGameUtility(self.setStr[0], CARD, True) +
                                child.strategy[1] * 1
                            )

                else:
                    # if player 1 plays pass...
                    self.utils[1] = 0
                    for CARD in CARDS:
                        if CARD != self.setStr[0]:
                            child = infoSets[CARD + actionStr]

                            # if player 2 plays pass
                            self.utils[1] += .5 * (
                                child.strategy[1] * getGameUtility(self.setStr[0], CARD, False)
                            )
                            # if player 2 plays bet
                            grandchild = infoSets[CARD + "pb"]
                            self.utils[1] += .5 * (
                                child.strategy[0] * grandchild.utility
                            )
                
        self.utility = self.strategy[0] * self.utils[0] + self.strategy[1] * self.utils[1]

    def setReachProbability(self):
        # if it's a root set, then it's just 1/3 
        if len(self.setStr) == 1:
            self.reach = 1/3

        # if it's player 2 playing
        elif len(self.setStr) == 2:
            self.reach = 0
            parentStrs = self.getParents()
            for parentStr in parentStrs:
                parent = infoSets[parentStr]
                self.reach += 1/3 * 1/2 * parent.strategy[ACTIONS.index(self.setStr[-1])]
        
        # if it's player 1 playing at turn 3
        else:
            self.reach = 0
            parentStrs = self.getParents()
            for parentStr in parentStrs:
                parent = infoSets[parentStr]
                self.reach += 1/3 * 1/2 * parent.strategy[0]

    def setGains(self):
        # if gain is < 0, set it to 0
        betGain = (self.utils[0] - self.utility) if (self.utils[0] - self.utility) * self.reach > 0 else 0
        passGain = (self.utils[1] - self.utility) if (self.utils[1] - self.utility) * self.reach > 0 else 0

        self.gainsSum[0] += betGain
        self.gainsSum[1] += passGain
        global cumulativeGains
        cumulativeGains += betGain + passGain


def debugPrintSets():
    headers = [
        "InfoSet","Strat:Bet", "Strat:Pass",
        "---","Belief:H", "Belief:L", "---",
        "Util:Bet","Util:Pass","ExpectedUtil",
        "Likelihood"
    ]
    rows=[]
    for infoSetStr in INFOSET_STRS:
        infoSet = infoSets[infoSetStr]
        row=[
            infoSetStr, *infoSet.strategy,
            infoSetStr, *infoSet.beliefs, infoSetStr,
            *infoSet.utils, infoSet.utility,
            infoSet.reach
        ]
        rows.append(row)
    print(tabulate(rows, headers=headers,tablefmt="pretty",stralign="left"))


def cfr():
    global infoSets
    # strategies
    for infoSetStr in INFOSET_STRS:
        infoSets[infoSetStr].setStrategies()

    # beliefs
    for infoSetStr in INFOSET_STRS:
        infoSets[infoSetStr].setBeliefs()
        # print(f"{infoSetStr}: {infoSets[infoSetStr].beliefs}")

    # utilities of each action, but go BACKWARDS
    for i in range(len(INFOSET_STRS) - 1, -1, -1):
        infoSets[INFOSET_STRS[i]].setUtils()
        # print(f"{INFOSET_STRS[i]}: {infoSets[INFOSET_STRS[i]].utils}")
        # also do reach probabilities while we're at it
        infoSets[INFOSET_STRS[i]].setReachProbability()

    # DEBUG PRINTING
    debugPrintSets()

    # update gains
    global cumulativeGains
    cumulativeGains = 0
    for infoSetStr in INFOSET_STRS:
        infoSets[infoSetStr].setGains()
        infoSets[infoSetStr].setStrategies()


def initSets():
    global infoSets
    for setStr in INFOSET_STRS:
        infoSets[setStr] = InfoSet(setStr)


def printResults():
    headers = [
        "InfoSet","Strat:Bet", "Strat:Pass",
        "---","Belief:H", "Belief:L", "---",
        "Util:Bet","Util:Pass","ExpectedUtil",
        "Likelihood","---","TotGain:Bet", "TotGain:Pass"
    ]
    rows=[]
    for infoSetStr in INFOSET_STRS:
        infoSet = infoSets[infoSetStr]
        row=[
            infoSetStr, *infoSet.strategy,
            infoSetStr, *infoSet.beliefs, infoSetStr,
            *infoSet.utils, infoSet.utility,
            infoSet.reach, infoSetStr, *infoSet.gainsSum
        ]
        rows.append(row)
    print(tabulate(rows, headers=headers,tablefmt="pretty",stralign="left"))


def main():
    # initialize info sets
    initSets()

    # begin actual computation
    for i in range(ITERATIONS):
        cfr()
        print(cumulativeGains)

    # print fine-tuned strategy
    # printResults()

if __name__ == "__main__":
    main()