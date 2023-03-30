from typing import NamedTuple

from entities.players import Player


class SidePot(NamedTuple):
    players: list[Player]
    size: float


class Pot:
    """Class that stores players contributions to the pot and implements the prize distribution"""
    def __init__(self, players: list[Player]):
        self.players = players.copy()
        self._contributions = {player: 0.0 for player in self.players}
        self.pot_size = 0.0
        self.pots: list[SidePot] = []

    def remove_player(self, player: Player):
        """remove player from the challengers"""
        self.players.remove(player)
        # we do not remove player's contribution to make pot recalculation easier

    def add_chips(self, player: Player, amount: float):
        """Save player's contribution and increase the pot"""
        self._contributions[player] += amount
        self.pot_size += amount

    def get_active_players(self):
        """list the players in the pot"""
        return self.players

    def unite_pots(self):
        """unite side pots with the same number of players"""
        # remove folded players from pots
        for side_pot in self.pots:
            for player in side_pot.players:
                if player not in self.players:
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
        contributions = sorted({size for _, size in self._contributions.items()})
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

    def distribute(self, rating: list[tuple[tuple, list[Player]]]):
        """
        pay prize money to the winners of each pot
        there may be multiple winners in multiple pots
        """
        # todo save or log the list of winners and their prizes
        for side_pot in self.pots:
            if len(side_pot.players) == 1:
                side_pot.players[0].add_money(side_pot.size)
            else:
                side_pot_winners: list[Player] = []
                for _, players in rating:
                    for player in players:
                        if player in side_pot.players:
                            side_pot_winners.append(player)

                    if side_pot_winners:
                        break

                prize = side_pot.size / len(side_pot_winners)
                for winner in side_pot_winners:
                    winner.add_money(prize)
