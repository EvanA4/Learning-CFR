import random


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


# Helper functions
def getGameUtility(pocket1: str, pocket2: str, isBet: bool):
    return (CARDS.index(pocket1) < CARDS.index(pocket2)) * (1 + isBet)


class InfoSet():
    def __init__(self, setStr: str) -> None:
        self.setStr = setStr
        self.gainsSum = [0, 0]
        self.strategy = [None, None]
        self.beliefs = [None, None]
        self.utils = [None, None]
        self.utility = None
        self.reach = None

    def getParents(self) -> list[str]:
        if (len(self.setStr) == 1):
            return []

        parents = []
        SUBSTR = self.setStr[1 : -1]
        for CARD in CARDS:
            if CARD != self.setStr[0]:
                parents.append(CARD + SUBSTR)

        return parents
    
    def setStrategies(self) -> None:
        total = self.gainsSum[0] + self.gainsSum[1]
        self.strategy[0] = self.gainsSum[0] / total
        self.strategy[1] = self.gainsSum[1] / total
    
    def setBeliefs(self) -> None:
        # split computation based on depth of node
        if len(self.setStr == 1):
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
            self.beliefs[0] = PROBS[0] / TOTAL
            self.beliefs[1] = PROBS[1] / TOTAL

    def setUtils(self) -> None:
        for ACTION in ACTIONS:
            # check if terminating
            actionStr = self.setStr[1:-1] + ACTION
            if actionStr in TERMINAL_ACTION_SET:
                parents = self.getParents()
                # add utility of both possible outcomes
                self.utils[ACTIONS.index(ACTION)] = self.beliefs[0] * getGameUtility(self.setStr[0], parents[0][0], actionStr[-1] == "b")
                self.utils[ACTIONS.index(ACTION)] += self.beliefs[1] * getGameUtility(self.setStr[0], parents[1][0], actionStr[-1] == "b")
            
            # check if second player is playing bet after player 1 played pass
            elif len(self.setStr) == 2:
                self.utils[0] = 0
                ctr = 0
                for CARD in CARDS:
                    if CARD != self.setStr[0]:
                        child = infoSets[CARD + actionStr]
                        self.utils[0] += self.beliefs[ctr] * (child.strategy[0] * getGameUtility(self.setStr[0], CARD, True))
                        self.utils[0] += self.beliefs[ctr] * (child.strategy[1] * getGameUtility(self.setStr[0], CARD, False))
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
                                child.strategy[0] + getGameUtility(self.setStr[0], CARD, True) +
                                child.strategy[1] + getGameUtility(self.setStr[0], CARD, False)
                            )

                else:
                    # if player 1 plays pass...
                    self.utils[1] = 0
                    for CARD in CARDS:
                        if CARD != self.setStr[0]:
                            child = infoSets[CARD + actionStr]

                            # if player 2 plays pass
                            self.utils[0] += .5 * (
                                child.strategy[0] + getGameUtility(self.setStr[0], CARD, False)
                            )
                            # if player 2 plays bet
                            self.utils[0] += .5 * (
                                child.strategy[0] + getGameUtility(self.setStr[0], CARD, False)
                            )

                
        self.strategy[0] * self.utils[0] + self.strategy[1] * self.utils[1]


            
            


    

def cfr():
    # strategies
    for infoSetStr in INFOSET_STRS:
        infoSets[infoSetStr].setStrategies()

    # beliefs
    for infoSetStr in INFOSET_STRS:
        infoSets[infoSetStr].setBeliefs()

    # utilities of each action, but go BACKWARDS
    for i in range(len(INFOSET_STRS) - 1, -1):
        infoSets[INFOSET_STRS[i]].setUtils()
        infoSets[INFOSET_STRS[i]].setUtility()

    # reach possibilities


    pass


def initSets():
    for setStr in INFOSET_STRS:
        infoSets[setStr] = InfoSet(setStr)


def main():
    # initialize info sets
    initSets()

    # begin actual computation
    for i in range(ITERATIONS):
        cfr()

    # print fine-tuned strategy


if __name__ == "__main__":
    main()

'''
TODO
1. if there's no parent, what are the beliefs?
2. utility
3. likelihood
4. gains
5. print results
'''