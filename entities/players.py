from typing import Any  # , Callable, Optional

from common.event import EventType, subscribe
from entities.bet import Bet, Decision
from entities.cards import Card
from errors import errors


class PlayerStatus:
    """Represents the player's status in the round"""
    def __init__(self, stack):
        self.__stack = stack
        self.last_move: Decision = Decision(Bet.NOT_DECIDED)

    def reset(self):
        """reset the last action. Should be called at the start of a round"""
        self.last_move = Decision(Bet.NOT_DECIDED)

    def reset_soft(self):
        """soft reset of the action. Should be used on the next stage"""
        if self.last_move.action not in (Bet.ALL_IN, Bet.FOLD):
            self.reset()
        else:
            self.last_move.size = 0

    def add_chips(self, amount):
        """add the chips to the stack"""
        self.__stack += amount

    def subtract_chips(self, amount):
        """take chips from the stack"""
        self.__stack -= amount

    @property
    def stack(self) -> float:
        """return the player's stack"""
        return self.__stack

    @property
    def is_active(self) -> bool:
        """Shows if the player is still in the game and participates in the prize distribution"""
        return (self.stack > 0 or self.last_move.action == Bet.ALL_IN) and not self.last_move.action == Bet.FOLD

    @property
    def is_all_in(self) -> bool:
        """Shows whether the player is all-in"""
        return self.last_move.action == Bet.ALL_IN

    def yet_to_move(self, bet_size) -> bool:
        """Shows whether player is yet to move"""
        return (self.last_move.size < bet_size or self.last_move.action == Bet.BLIND) \
            and not self.last_move.action == Bet.ALL_IN

    def get(self) -> dict:
        """dict representation"""
        return {
            "stack": self.stack,
            "last_move": self.last_move,
        }

    def bet(self, amount):
        """Place a bet"""
        if amount:
            diff = amount - self.last_move.size
            if diff >= self.stack:
                amount = self.stack + self.last_move.size
                self.last_move = Decision(Bet.ALL_IN, amount)
            self.subtract_chips(diff)
            if self.stack <= 0:
                self.__stack = 0

    def post_blind(self, amount):
        """Place a blind without marking player as having decided"""
        self.bet(amount)
        if not self.is_all_in:
            self.last_move = Decision(Bet.BLIND, amount)


class Hand:
    def __init__(self):
        self.__cards: list[Card] = []

    def add_card(self, card):
        """Add a pocket card. Must be used by the game only"""
        if len(self.__cards) == 2:
            raise errors.TooManyCards('The hand is full')
        self.__cards.append(card)

    def reset(self):
        self.__cards = []

    def get(self) -> tuple[Card]:
        return tuple(self.__cards)


class Player:
    """
    Player entity.
    Implements player's pocket_cards and bets making
    """

    def __init__(self, start_stack: float, is_ai: bool = True, name: str = ''):
        self.__hand = Hand()
        self.__IS_AI: bool = is_ai
        self.NAME: str = name
        self.status = PlayerStatus(start_stack)

    def __repr__(self):
        return f"{self.NAME}({'AI' if self.is_ai else 'human'})"

    def reset(self):
        self.__hand.reset()
        self.status.reset()

    @property
    def hand(self) -> tuple[Card]:
        """Player's pocket cards"""
        return self.__hand.get() if self.status.is_active else ()

    def add_card(self, card: Card):
        self.__hand.add_card(card)

    def get_reduced_status(self) -> dict:
        """Shows less data in more readable way"""
        return {"name": self.NAME} | self.status.get()

    @property
    def is_ai(self) -> bool:
        """Shows whether player is AI"""
        return self.__IS_AI


class Account:
    """Account, statistics, an interface to login, join games and buy stack"""

    def __init__(self, name):
        self.name = name
        self._chips_amount: float = 0.0
        self.games: dict[Any: Player] = {}

    def buy_chips(self, amount: float):
        """Add the amount of chips to the account"""
        self._chips_amount += amount

    def join_game(self, game, buy_in):
        """Join a game with the amount of chips"""
        if game in self.games.keys():
            raise errors.AlreadyInTheGame

        if buy_in > self._chips_amount:
            raise errors.NotEnoughMoney

        player = Player(buy_in, name=self.name)
        self._chips_amount -= buy_in
        self.games |= {game: player}
        return player

    def leave_game(self, game):
        """leave the game passing chips from the player's stack to the account"""
        if game not in self.games:
            raise errors.GameNotFoundError

        player: Player = self.games[game]
        self._chips_amount += player.status.stack
        self.games.pop(game)


subscribe(EventType.PLAYER_MOVED, Player.get_reduced_status)
