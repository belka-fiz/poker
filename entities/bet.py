from enum import Enum


class Bet(Enum):
    NOT_DECIDED = 0
    FOLD = 1
    CHECK = 2
    CALL = 3
    RAISE = 4
    ALL_IN = 5
    BLIND = 6


class Decision:
    def __init__(self,
                 action: Bet,
                 size: float = 0):
        self.action = action
        self.size = size
