from enum import Enum


class Bet(Enum):
    """Enum for bet actions"""

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
    """Player's decision, that consists of bet action and the amount of the bet"""

    def __init__(self,
                 action: Bet,
                 size: float = 0):
        if not isinstance(action, Bet):
            raise ValueError('Action must be a Bet object')
        self.action = action
        self.size = size

    def __eq__(self, other):
        return self.action == other.action and self.size == other.size

    def __hash__(self):
        return self.size + hash(self.action)
