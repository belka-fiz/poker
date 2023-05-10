from pprint import PrettyPrinter

from entities.players import Player
from entities.round import Round
from .interface import View


class CliView(View):
    def __init__(self):
        self.pp = PrettyPrinter(indent=2, sort_dicts=False)

    @staticmethod
    def last_move(player: Player):
        """print player's last move"""
        print(player.get_reduced_status())

    @staticmethod
    def print_board(board, pot):
        """print the state of the board and the pot"""
        print(f"\nThe board: {board}, the pot: {pot.pot_size}")

    def print_winners(self, game_round: Round):
        """Print winners rating and pot distribution"""
        if len(game_round.active_players) > 1:
            print("\nPlayers' hands:")
            self.pp.pprint({player: player.hand for player in game_round.active_players})
        print("\nRound rating:")
        self.pp.pprint(game_round.rating)
        print("\nPots distribution:")
        self.pp.pprint(game_round.pot.winners)
        print('\n')

    def print_round_stats(self, game_round: Round):
        """Print round end stats"""
        self.pp.pprint(game_round.end_stats())
        print()
