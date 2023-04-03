class UnavailableDecision(BaseException):
    """Player can't choose this decision"""

    pass


class TooManyCards(BaseException):
    """No more cards can be dealt to the player"""

    pass


class NegativeBetError(BaseException):
    """Player can't make a move with negative bet"""

    pass


class NotEnoughPlayers(BaseException):
    """Game can not be started or continued with this number of players"""

    pass


class NotEnoughMoney(BaseException):
    """Player does not have enough money to join or continue the game"""

    pass


class AlreadyInTheGame(BaseException):
    """Player can not be added to the game as long as they are already in the game"""

    pass


class GameNotFoundError(BaseException):
    """The game can not be joined or called because it's not found"""

    pass


class TooSmallBetError(BaseException):
    """Player can't post a bet smaller than the current one except all-in"""

    pass
