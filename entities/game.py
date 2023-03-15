from operator import itemgetter
from typing import Iterable

from ai.ai import PreFlopDecider, StageBetAI
from controller.cli import game_cli_action
from entities.cards import Deck, Card
from entities.combinations import best_hand, Combination
from entities.players import Player, Account
from errors.errors import NotEnoughPlayers, UnavailableDecision, TooSmallBetError


class Game:
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


class Round:
    STAGES = ('deal', 'pre-flop', 'flop', 'turn', 'river', 'showdown')
    NUMBER_OF_CARDS = {1: 0, 2: 3, 3: 1, 4: 1}  # how many cards to open on each stage

    def __init__(self, players: list[Player], dealer_index: int, blind_size: float):
        """Initialize the game"""
        self.blind_size = blind_size
        self._board: list[Card] = []
        self.pot: float = 0.0
        self.winners: list[Player] = []
        self.deck = Deck()
        self.players = players[dealer_index + 1:] + players[:dealer_index + 1]
        self._stage_index = 0
        self._deal_players_cards()
        self._new_stage()

    @property
    def board(self):
        return tuple(self._board)

    def _deal_board(self, number: int):
        """deal number of cards to board"""
        self.deck.hide_one()
        self._board.extend([self.deck.draw_one() for _ in range(number)])

    def _new_stage(self):
        self._stage_index += 1
        self._deal_board(self.NUMBER_OF_CARDS[self._stage_index])
        print(f"The board: {self.board}, the pot: {self.pot}")  # todo replace with log OR view call
        for player in self._active_players:  # reset each player's status
            player.new_stage()

        # post blinds if pre-flop
        if self._stage_index == 1:
            for i in range(2):
                amount = self.blind_size / 2 * (1 + i)
                self._active_players[i].post_blind(amount)
                print(self._active_players[i].get_status())  # todo replace with log of the last move
            self._bets_round(self.players[1])
        else:
            self._bets_round()

        # find winners if necessary or proceed to the next stage
        if self._number_of_players_left == 1 or self._stage_index == 4:
            if not self.winners:
                self._end()
        else:
            self._new_stage()

    @property
    def _active_players(self):
        return [player for player in self.players if player.is_active]

    @property
    def _number_of_players_left(self):
        return len(self._active_players)

    @property
    def max_bet(self):
        return max(player.get_bet for player in self.players)

    def _update_queue(self, last_raiser: Player):
        """make a queue of players to move after the last raiser"""
        try:
            index = self._active_players.index(last_raiser)
        except ValueError:
            index = 0
        return self._active_players[index + 1:] + self._active_players[:index + 1]

    def _turns_queue(self, last_raiser: Player) -> Iterable[Player]:
        """get the next player to move"""
        while not_decided := [player for player in self._update_queue(last_raiser) if not player.made_decision]:
            if len([player for player in self._active_players if not player.is_all_in]) == 1 and not self.max_bet:
                break
            yield not_decided[0]

    def _bets_round(self, last_raiser: Player = None):
        # reset each player's decision except the last raiser and the ones who are all-in
        for player in self._active_players:
            if player is not last_raiser and not player.is_all_in:
                player.reset_decision()

        # cycle through players and ask for a decision
        for player in self._turns_queue(last_raiser):
            current_max_bet = self.max_bet
            player.ask_for_a_decision(current_max_bet)
            if player.is_ai:  # todo replace with Player interface. Remove AI logic from here
                if self._stage_index == 1:
                    decider = PreFlopDecider(player)
                    ai_decisions = decider.decision()
                    try:
                        decision = [d for d in ai_decisions if d in player.available_decisions][0]
                    except IndexError:
                        print(f"Something went wrong")
                        print(f"Player's available decisions: {player.available_decisions}")
                        print(f"AI's suggested decisions: {ai_decisions}")
                        raise UnavailableDecision
                    amount = decider.how_much_to_bet(self.blind_size, current_max_bet)
                    try:
                        player.decide(decision, amount)
                    except TooSmallBetError as e:
                        print(f"{self.max_bet=}, {player.stack=}, "
                              f"{player.requested_bet=}, {player.available_decisions=}, "
                              f"{player.get_bet=}, {decision=}, {amount=}")
                        raise e
                else:
                    decider = StageBetAI(self.board, player, self.blind_size, self._number_of_players_left)
                    ai_decisions = decider.should_i_bet(current_max_bet)
                    try:
                        decision = [d for d in ai_decisions if d in player.available_decisions][0]
                    except IndexError:
                        print(f"Something went wrong")
                        print(f"Player's available decisions: {player.available_decisions}")
                        print(f"AI's suggested decisions: {ai_decisions}")
                        raise UnavailableDecision
                    player.decide(decision, decider.how_much_to_bet(current_max_bet))
                print(player.get_status())
            else:
                game_cli_action(player, self._board, current_max_bet)
            if player.get_bet > current_max_bet:
                last_raiser = player
                self._bets_round(last_raiser)
                return
        self._update_bank()
        if self._number_of_players_left == 1 and not self.winners:
            self._end()

    def _deal_players_cards(self):
        """just deal cards starting from the next after dealer"""
        for player in self.players:
            player.new_game_round()
        for _ in range(2):
            for player in self._active_players:
                player.add_card(self.deck.draw_one())

    def _update_bank(self):
        """collect all bets after each stage"""
        self.pot += sum([player.get_bet for player in self.players])
        for player in self.players:  # reset each player's bank as soon as we collected it
            player.new_stage()

    def _find_winners(self):
        print(f"current_players: {self.players}, pot: {self.pot}")
        if self._number_of_players_left == 1:
            self.winners = [self._active_players[0]]
            return
        else:
            self._stage_index += 1
            show_downs = tuple(player.show_down() for player in self._active_players)
            players_combs: list[tuple[int, tuple[Combination, tuple]]] = \
                list(enumerate(best_hand(sd + self.board) for sd in show_downs))
            combinations = sorted(players_combs, key=itemgetter(1), reverse=True)
            winners = []
            for i, comb in players_combs:
                if comb == combinations[0][1]:
                    winners.append(self._active_players[i])
            self.winners = winners

    def _calculate_prize(self):
        # todo add logic for bets over someone's all-in
        if len(self.winners) <= 1:
            return self.pot
        else:
            return self.pot / len(self.winners)

    def _end(self):
        self._find_winners()
        prize = self._calculate_prize()
        for winner in self.winners:
            winner.add_money(prize)
        print(self.get_status())

    # def close_round(self):
    #     for player in self.players:
    #         player.new_game_round()
    #     self.pot = 0

    def get_status(self):
        """return current game stage, players statuses, the bank and the table"""
        return {
            'stage': self.STAGES[self._stage_index],
            'board': self.board,
            'players': [player.get_status() for player in self.players]
        }
