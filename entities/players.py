from typing import Any

from entities.cards import Card
from entities.bet import Bet, Decision
from errors import errors


class Player:
    def __init__(self, start_stack: float, is_ai: bool = True, name: str = ''):
        self.__stack = start_stack
        self.__hand: list[Card] = []
        self.__all_in: bool = False
        self._in_the_game: bool = True
        self._made_decision: bool = False
        self.available_actions: list[Bet] = []
        self.requested_bet: float = 0
        self.__is_ai: bool = is_ai
        self.name: str = name
        self.decision: Decision = Decision(Bet.NOT_DECIDED)

    # resets
    def _reset_status(self):
        """reset bet status except all_in"""
        if self.__all_in:
            self.decision.size = 0  # walkaround for current_bet resets
        else:
            self._made_decision = False
            self.decision = Decision(Bet.NOT_DECIDED)
        self.available_actions = []
        self.requested_bet = 0

    def new_stage(self):
        self._reset_status()

    def new_game_round(self):
        """reset everything"""
        self._reset_status()
        self.__hand: list[Card] = []
        self.__all_in = False
        if self.__stack > 0:
            self._in_the_game = True

    # bets
    def _bet(self, amount):
        if amount:
            diff = amount - self.decision.size
            if diff >= self.__stack:
                self.__all_in = True
                amount = self.__stack + self.decision.size
                self.decision = Decision(Bet.ALL_IN, amount)
            self.__stack -= diff
            if self.__stack <= 0:
                self.__stack = 0

    def post_blind(self, amount):
        self._bet(amount)
        if self.__all_in:
            self._made_decision = True
        else:
            self.decision = Decision(Bet.BLIND, amount)

    @property
    def is_all_in(self):
        return self.__all_in

    # cards
    def add_card(self, card):
        """must be used by the game"""
        if len(self.__hand) == 2:
            raise errors.TooManyCards('The hand is full')
        else:
            self.__hand.append(card)

    @property
    def hand(self):
        # todo think about the security
        return tuple(self.__hand)

    def get_status(self):
        data = {
            'name': self.name,
            'in_game': self._in_the_game,
            'last_decision': self.decision.action.name.capitalize(),
            'current_bet': self.decision.size,
            'all_in': self.__all_in,
            'money': self.__stack,
            'made_decision': self._made_decision
        }
        return data

    @property
    def is_active(self):
        return self._in_the_game

    # decisions
    @property
    def made_decision(self):
        return self._made_decision

    def reset_decision(self):
        self._made_decision = False

    def ask_for_a_decision(self, requested_bet=0.0):
        if not requested_bet or requested_bet == self.decision.size:
            self.available_actions = [Bet.CHECK, Bet.FOLD, Bet.RAISE, Bet.ALL_IN]
        elif requested_bet < self.__stack + self.decision.size:
            self.available_actions = [Bet.FOLD, Bet.CALL, Bet.RAISE, Bet.ALL_IN]
        elif requested_bet == self.__stack + self.decision.size:
            self.available_actions = [Bet.FOLD, Bet.CALL, Bet.ALL_IN]
        else:
            self.available_actions = [Bet.FOLD, Bet.ALL_IN]
        self.requested_bet = requested_bet
        return self.available_actions

    def decide(self, decision: Decision):
        """an interface for bets"""
        action = decision.action
        if action not in self.available_actions:
            error_msg = f'Decision {decision} is not available. Must choose from: {self.available_actions}'
            raise errors.UnavailableDecision(error_msg)
        if decision.size < 0:
            raise errors.NegativeBetError
        elif action == Bet.CHECK:
            self.decision.action = Bet.CHECK
        elif action == Bet.FOLD:
            self.decision.action = Bet.FOLD
            self.__hand = []
            self._in_the_game = False
        elif action == Bet.CALL:
            self._bet(self.requested_bet)
            self.decision = Decision(Bet.CALL, self.requested_bet)
        elif action == Bet.RAISE:
            if decision.size < self.requested_bet:
                raise errors.TooSmallBetError
            self._bet(decision.size)
            if not self.__all_in:
                if decision.size == self.requested_bet:
                    self.decision = Decision(Bet.CALL, decision.size)
                else:
                    self.decision = decision
        elif action == Bet.ALL_IN:
            self._bet(self.__stack + self.decision.size)
        self._made_decision = True

    # money
    def add_money(self, amount):
        """when player buys credit or wins"""
        self.__stack += amount

    @property
    def stack(self):
        return self.__stack

    @property
    def is_ai(self) -> bool:
        return self.__is_ai


class Account:
    """account, statistics, an interface to login, join games and buy stack"""
    def __init__(self, name):
        self.name = name
        self._chips_amount: float = 0.0
        self.games: dict[Any: Player] = {}

    def buy_chips(self, amount: float):
        self._chips_amount += amount

    def join_game(self, game, buy_in):
        if game in self.games.keys():
            raise errors.AlreadyInTheGame
        if buy_in > self._chips_amount:
            raise errors.NotEnoughMoney
        player = Player(buy_in, name=self.name)
        self._chips_amount -= buy_in
        self.games |= {game: player}

    def leave_game(self, game):
        if game not in self.games:
            raise errors.GameNotFoundError
        else:
            player: Player = self.games[game]
            self._chips_amount += player.stack
            self.games.pop(game)
