from abc import ABC, abstractmethod

from common.event import subscribe, EventType
from entities.players import Player
from entities.round import Round


class View(ABC):
    """Abstract class for data output"""

    @staticmethod
    @abstractmethod
    def last_move(player: Player):
        """Display last move of a player"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def print_board(board, pot):
        """Display the status of board and the pot"""
        raise NotImplementedError

    @abstractmethod
    def print_winners(self, game_round: Round):
        """Display winners, their hands, rating and pots distribution"""
        raise NotImplementedError

    @abstractmethod
    def print_round_stats(self, game_round: Round):
        """Display round end stats"""
        raise NotImplementedError


def subscribe_view(view: View):
    _view = view()  # noqa
    subscribe(EventType.PLAYER_MOVED, _view.last_move)
    subscribe(EventType.NEW_STAGE, _view.print_board)
    subscribe(EventType.WINNERS_CALCULATED, _view.print_winners)
    subscribe(EventType.ROUND_END, _view.print_round_stats)
