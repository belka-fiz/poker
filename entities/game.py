from entities.players import Player, Account
from entities.round import Round
from errors.errors import NotEnoughPlayers


class Game:
    """
    A game of many rounds.
    Has logic of game initiation, adding or removing players, blind raises and Round initiation
    """

    def __init__(self, blind: float, buy_in: float, continuous: bool = False):
        self.initial_blind = blind  # set initial size of blind bets
        self.buy_in = buy_in  # set initial chips on the game start
        self.continuous = continuous  # enable auto top-up for AI players
        self.blind: float = 0.0  # set actual blind size
        self.increase_blinds = 5  # number of round after which the blinds are doubled  # todo make customizable
        self.players: list[Player] = []  # init players list
        self.last_dealer_index: int = -1  # init dealer's position
        self.rounds_started = 0  # init rounds counter. Used for blinds raises

    def add_human_player(self, account: Account):
        account.join_game(self, self.buy_in)
        # not used yet. Accounts are to be implemented

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players.pop(self.players.index(player))

    def raise_blind(self):
        self.blind = self.initial_blind * 2 ** (self.rounds_started // self.increase_blinds)

    def new_round(self):
        # kick bankrupt players or add money for AI
        for player in self.players:
            if player.stack <= 0:
                if not self.continuous or not player.is_ai:
                    self.remove_player(player)
                elif player.is_ai:
                    player.add_money(self.buy_in)

        # raise an exception if no players left
        if len(self.players) < 2:
            raise NotEnoughPlayers

        # update blinds and start a new round
        self.raise_blind()
        new_round = Round(self.players, self.last_dealer_index, self.blind)

        # cycle dealer
        self.last_dealer_index += 1
        if self.last_dealer_index >= len(self.players):
            self.last_dealer_index = 0

        self.rounds_started += 1
        return new_round

    def end_game(self):
        # do I need it?
        pass
