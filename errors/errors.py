class UnavailableDecision(BaseException):
    """Player can't choose this decision"""


class TooManyCards(BaseException):
    """No more cards can be dealt to the player"""


class NegativeBetError(BaseException):
    """Player can't make a move with negative bet"""


class NotEnoughPlayers(BaseException):
    """Game can not be started or continued with this number of players"""


class NotEnoughMoney(BaseException):
    """Player does not have enough money to join or continue the game"""


class AlreadyInTheGame(BaseException):
    """Player can not be added to the game as long as they are already in the game"""


class GameNotFoundError(BaseException):
    """The game can not be joined or called because it's not found"""


class TooSmallBetError(BaseException):
    """Player can't post a bet smaller than the current one except all-in"""


class WrongSuit(ValueError):
    """Tried to find a suit by wrong short name"""


class WrongValue(ValueError):
    """Tried to find a value by wrong short name"""


class WrongAlias(ValueError):
    """Tried to get a card with wrong alias and/or unavailable suit or value"""
