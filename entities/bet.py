from enum import Enum


class Bet(Enum):
    NOT_DECIDED = 'Not decided'
    FOLD = 'Fold'
    CHECK = 'Check'
    CALL = 'Call'
    RAISE = 'Raise'
    ALL_IN = 'All-in'
    BLIND = 'Blind'

    def __repr__(self):
        return self.value


class Decision:
    def __init__(self,
                 action: Bet,
                 size: float = 0):
        assert isinstance(action, Bet)
        self.action = action
        self.size = size

    def __eq__(self, other):
        return self.action == other.action and self.size == other.size
