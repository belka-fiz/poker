from typing import Callable, Optional

from common.event import subscribe, EventType
from errors import errors
from .bet import Bet, Decision
from .players import Player, PlayerStatus


class BetProcessor:
    """Process players bets"""
    def __init__(self, player: Player, requested_bet: float):
        self.player: Player = player
        self.p_stats: PlayerStatus = player.status
        self.available_actions = []
        self.requested_bet = 0
        self.ask_for_a_decision(requested_bet)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def ask_for_a_decision(self, requested_bet=0.0):
        """Update available actions for player to make"""
        if not requested_bet or requested_bet == self.p_stats.last_move.size:
            self.available_actions = [Bet.CHECK, Bet.FOLD, Bet.RAISE, Bet.ALL_IN]
        elif requested_bet < self.p_stats.stack + self.p_stats.last_move.size:
            self.available_actions = [Bet.FOLD, Bet.CALL, Bet.RAISE, Bet.ALL_IN]
        elif requested_bet == self.p_stats.stack + self.p_stats.last_move.size:
            self.available_actions = [Bet.FOLD, Bet.CALL, Bet.ALL_IN]
        else:
            self.available_actions = [Bet.FOLD, Bet.ALL_IN]
        self.requested_bet = requested_bet
        return self.available_actions

    def process_check(self):
        self.p_stats.last_move.action = Bet.CHECK

    def process_fold(self):
        self.p_stats.last_move.action = Bet.FOLD

    def process_call(self):
        self.p_stats.bet(self.requested_bet)
        self.p_stats.decision = Decision(Bet.CALL, self.requested_bet)

    def process_raise(self, amount: float):
        if amount < self.requested_bet:
            raise errors.TooSmallBetError

        self.p_stats.bet(amount)
        if not self.p_stats.is_all_in:
            if amount == self.requested_bet:
                if self.requested_bet == 0:
                    self.p_stats.decision = Decision(Bet.CHECK)
                else:
                    self.p_stats.decision = Decision(Bet.CALL, amount)
            else:
                self.p_stats.decision = Decision(Bet.RAISE, amount)

    def process_all_in(self):
        self.p_stats.bet(self.p_stats.stack + self.p_stats.last_move.size)

    def process_bet(self, action: Bet, *args: float) -> None:
        functions: dict[Bet: Callable[[Bet, Optional[float]], None]] = {
            Bet.CHECK: self.process_check,
            Bet.FOLD: self.process_fold,
            Bet.CALL: self.process_call,
            Bet.RAISE: self.process_raise,
            Bet.ALL_IN: self.process_all_in
        }
        functions[action](*args)  # noqa

    def decide(self, decision: Decision):
        """An interface for bet processing"""
        action = decision.action
        if action not in self.available_actions:
            error_msg = f'Decision {decision} is not available. Must choose from: {self.available_actions}'
            raise errors.UnavailableDecision(error_msg)

        if decision.size < 0:
            raise errors.NegativeBetError

        if action == Bet.RAISE:
            args = [decision.size]
        else:
            args = []
        self.process_bet(action, *args)

        self.p_stats._made_decision = True


subscribe(EventType.PLAYER_PREPARE_MOVE, BetProcessor.ask_for_a_decision)
