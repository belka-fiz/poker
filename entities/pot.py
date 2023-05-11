from typing import NamedTuple

from entities.players import Player


class SidePot(NamedTuple):
    """Just stores the list of players in a side pot and its size"""

    players: list[Player]
    size: float

    def __hash__(self):
        return id(self.players)


class Pot:
    """Class that stores players contributions to the pot and implements the prize distribution"""

    def __init__(self, players: list[Player]):
        self._players = players.copy()
        self._contributions = {player: 0.0 for player in self._players}
        self.pot_size = 0.0
        self.pots: list[SidePot] = []
        self.winners: dict[SidePot: dict[Player: float]] = {}

    @property
    def players(self):
        return [player for player in self._players if player.is_active]

    def remove_player(self, player: Player):
        """remove player from the challengers"""
        self._players.remove(player)
        # we do not remove player's contribution to make pot recalculation easier

    def add_chips(self, player: Player, amount: float):
        """Save player's contribution and increase the pot"""
        self._contributions[player] += amount
        self.pot_size += amount

    def unite_pots(self):
        """unite side pots with the same number of players"""
        # remove folded players from pots
        for side_pot in self.pots:
            players_to_remove: list[Player] = []
            for player in side_pot.players:
                if player not in self.players:
                    players_to_remove.append(player)
            for player in players_to_remove:
                side_pot.players.remove(player)

        # unite the pots with the same number of players
        pots_by_players_num = {num: [] for num in {len(pot.players) for pot in self.pots}}
        for num in pots_by_players_num:
            pots_by_players_num[num] = [pot for pot in self.pots if len(pot.players) == num]
        new_pots = [SidePot(pots[0].players, sum(pot.size for pot in pots)) for _, pots in pots_by_players_num.items()]
        new_pots.sort(key=lambda p: len(p.players), reverse=True)
        self.pots = new_pots

    def recalculate_pots(self):
        """calculate side pots according to players' contributions to the pot"""
        self.pots = []
        contributions = sorted({size for _, size in self._contributions.items() if size > 0})
        if len(contributions) == 1:
            self.pots = [SidePot(self.players, self.pot_size)]
            return

        last_contribution = 0
        for contribution in contributions:
            players = [player for player, contr in self._contributions.items() if contr >= contribution]
            players_in_the_pot = len(players)
            pot_size = players_in_the_pot * contribution
            new_pot = SidePot(players, pot_size - last_contribution * players_in_the_pot)
            self.pots.append(new_pot)
            last_contribution = contribution
        self.unite_pots()

    def pay_wins(self):
        """Method to pay winners separately from defining the sizes of wins"""
        for _, winners_list in self.winners.items():
            for winner, prize in winners_list.items():
                winner.add_money(prize)

    def distribute(self, rating: list[tuple[tuple, list[Player]]]):
        """
        define the winners of each pot
        decide how much money to pay the winners of each pot
        there may be multiple winners in multiple pots
        """
        for side_pot in self.pots:
            # case 1 player in the pot - make him winner
            if len(side_pot.players) == 1:
                self.winners[side_pot] = {side_pot.players[0]: side_pot.size}
                continue

            # case multiple players in the pot
            side_pot_winners: list[Player] = []
            for _, winners in rating:
                for winner in winners:
                    if winner in side_pot.players:
                        side_pot_winners.append(winner)
                if side_pot_winners:
                    break

            prize = side_pot.size / len(side_pot_winners)
            self.winners[side_pot] = {_winner: prize for _winner in side_pot_winners}
