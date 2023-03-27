from typing import Any

from entities.cards import Card
from entities.bet import Bet, Decision
from errors import errors


class Player:
    def __init__(self, start_stack: float, is_ai: bool = True, name: str = ''):
        self.__stack = start_stack
        self.__hand: list[Card] = []
        self.__all_in = False
        self._in_the_game = True
        self._made_decision = False
        self.available_decisions = []
        self.requested_bet = 0
        self.__is_ai = is_ai
        self.name = name
        self.bet: Decision = Decision(Bet.NOT_DECIDED)

    # resets
    def _reset_status(self):
        """reset bet status except all_in"""
        if self.__all_in:
            self.bet.size = 0  # walkaround for current_bet resets
        else:
            self._made_decision = False
            self.bet = Decision(Bet.NOT_DECIDED)
        self.available_decisions = []
        self.requested_bet = 0

    def new_stage(self):
        self._reset_status()

    def new_game_round(self):
        self._reset_status()
        self.__hand: list[Card] = []
        self.__all_in = False
        if self.__stack > 0:
            self._in_the_game = True

    # bets
    def _bet(self, amount):
        if amount:
            diff = amount - self.bet.size
            if diff >= self.__stack:
                self.__all_in = True
                amount = self.__stack + self.bet.size
                self.bet = Decision(Bet.ALL_IN, amount)
            self.__stack -= diff
            if self.__stack <= 0:
                self.__stack = 0

    def post_blind(self, amount):
        self._bet(amount)
        if self.__all_in:
            self._made_decision = True
        else:
            self.bet = Decision(Bet.BLIND, amount)

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
            'last_decision': self.bet.action.name.capitalize(),
            'current_bet': self.bet.size,
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
        # todo rewrite with enum
        if not requested_bet or requested_bet == self.bet.size:
            self.available_decisions = ['check', 'fold', 'raise', 'all_in']
        elif requested_bet < self.__stack + self.bet.size:
            self.available_decisions = ['fold', 'call', 'raise', 'all_in']
        elif requested_bet == self.__stack + self.bet.size:
            self.available_decisions = ['fold', 'call', 'all_in']
        else:
            self.available_decisions = ['fold', 'all_in']
        self.requested_bet = requested_bet
        return self.available_decisions

    def decide(self, decision, amount=0.0):
        """an interface for bets"""
        # todo rewrite with enum
        if decision not in self.available_decisions:
            error_msg = f'Decision {decision} is not available. Must choose from: {self.available_decisions}'
            raise errors.UnavailableDecision(error_msg)
        if amount < 0:
            raise errors.NegativeBetError
        elif decision == 'check':
            self.bet.action = Bet.CHECK
        elif decision == 'fold':
            self.bet.action = Bet.FOLD
            self.__hand = []
            self._in_the_game = False
        elif decision == 'call':
            self._bet(self.requested_bet)
            self.bet = Decision(Bet.CALL, self.requested_bet)
        elif decision == 'raise':
            if amount < self.requested_bet:
                raise errors.TooSmallBetError
            self._bet(amount)
            if not self.__all_in:
                if amount == self.requested_bet:
                    self.bet = Decision(Bet.CALL, amount)
                else:
                    self.bet = Decision(Bet.RAISE, amount)
        elif decision == 'all_in':
            self._bet(self.__stack + self.bet.size)
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
