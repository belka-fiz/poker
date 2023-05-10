from abc import ABC, abstractmethod

from common.event import subscribe, EventType
from entities.players import Player
from entities.round import Round


class View(ABC):
    @staticmethod
    @abstractmethod
    def last_move(player: Player):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def print_board(board, pot):
        raise NotImplementedError

    @abstractmethod
    def print_winners(self, game_round: Round):
        raise NotImplementedError

    @abstractmethod
    def print_round_stats(self, game_round: Round):
        raise NotImplementedError


def subscribe_view(view: View):
    _view = view()  # noqa
    subscribe(EventType.PLAYER_MOVED, _view.last_move)
    subscribe(EventType.NEW_STAGE, _view.print_board)
    subscribe(EventType.WINNERS_CALCULATED, _view.print_winners)
    subscribe(EventType.ROUND_END, _view.print_round_stats)
