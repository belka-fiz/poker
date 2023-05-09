from pprint import PrettyPrinter
from typing import Iterable, Union

from ai.ai import AI
from controller.cli import game_cli_action
from entities.cards import Card, Deck
from entities.combinations import Combination, best_hand
from entities.players import Player
from entities.pot import Pot

pp = PrettyPrinter(indent=2, sort_dicts=False)


class Round:
    """
    The implementation of game round logic including:
    - cards distribution to players
    - round stages with dealing the community cards
    - blinds posting and betting cycles
    - determining the rating of players' combinations
    """

    STAGES = ('deal', 'pre-flop', 'flop', 'turn', 'river', 'showdown')
    # how many cards to open on each stage
    NUMBER_OF_CARDS = {
        1: 0,  # pre-flop
        2: 3,  # flop
        3: 1,  # turn
        4: 1,  # river
        5: 0   # showdown
    }

    def __init__(self, players: list[Player], dealer_index: int, blind_size: float, debug: bool = False):
        """Initialize the game"""
        self.players: list[Union[Player, AI]] = players[dealer_index + 1:] + players[:dealer_index + 1]
        self.blind_size = blind_size
        self.debug = debug

        self.deck = Deck()
        self._board: list[Card] = []
        self._stage_index = 0
        self.pot: Pot = Pot(self.players)
        self.rating = []

        if not self.debug:
            self.deal_players_cards()
            self.new_stage()

    @property
    def board(self):
        """Provide the community cards, or the board"""
        return tuple(self._board)

    def _deal_board(self, number: int):
        """Deal the number of cards to the board"""
        self.deck.hide_one()
        self._board.extend([self.deck.draw_one() for _ in range(number)])

    def new_stage(self):
        """New cards are dealt, players make their bets"""
        self._stage_index += 1
        self._deal_board(self.NUMBER_OF_CARDS[self._stage_index])
        print(f"The board: {self.board}, the pot: {self.pot.pot_size}")  # todo replace with log OR view call
        for player in self.active_players:  # reset each player's status
            player.new_stage()

        # post blinds if pre-flop
        if self._stage_index == 1:
            for i in range(2):
                amount = self.blind_size / 2 * (1 + i)
                self.active_players[i].post_blind(amount)
                print(self.active_players[i].get_reduced_status())  # todo replace with log or view call
            if not self.debug:
                self._bets_round(self.players[1])
        elif not self.debug:
            self._bets_round()

        if not self.debug:
            # find winners if necessary or proceed to the next stage
            if self._number_of_players_left == 1 or self._stage_index == 4:
                self._end()
            else:
                self.new_stage()

    @property
    def active_players(self) -> list[Player, AI]:
        """Provides the list of players who haven't folded"""
        return [player for player in self.players if player.is_active]

    @property
    def _number_of_players_left(self):
        """Number of players left in the game(not folded)"""
        return len(self.active_players)

    @property
    def max_bet(self):
        """The size of the biggest bet in the current game stage"""
        return max(player.decision.size for player in self.players)

    def _update_queue(self, last_raiser: Player) -> list[Player]:
        """make a queue of players to move after the last raiser"""
        try:
            index = self.active_players.index(last_raiser)
        except ValueError:
            index = -1
        return self.active_players[index + 1:] + self.active_players[:index + 1]

    def _turns_queue(self, last_raiser: Player) -> Iterable[Union[Player, AI]]:
        """get the next player to move"""
        while not_decided := [player for player in self._update_queue(last_raiser) if not player.made_decision]:
            if len([player for player in self.active_players if not player.is_all_in]) == 1 and not self.max_bet:
                break
            yield not_decided[0]

    def _bets_round(self, last_raiser: [Player, AI] = None):
        """cycle through active players and get players' moves"""
        # reset each player's decision except the last raiser and the ones who are all-in
        for player in self.active_players:
            if player is not last_raiser and not player.is_all_in:
                player.reset_decision()

        # cycle through players and ask for a decision
        for player in self._turns_queue(last_raiser):
            current_max_bet = self.max_bet
            player.ask_for_a_decision(current_max_bet)
            if isinstance(player, AI):
                player.make_a_move(self.board,
                                   current_max_bet,
                                   self._stage_index,
                                   self.blind_size,
                                   self._number_of_players_left)
            else:
                game_cli_action(player, self._board, current_max_bet)

            print(player.get_reduced_status())  # todo replace with log or view call
            if player.decision.size > current_max_bet:
                last_raiser = player
                self._bets_round(last_raiser)
                return
        self._update_bank()

    def deal_players_cards(self):
        """just deal cards starting from the next after dealer"""
        for player in self.players:
            player.new_game_round()
        for _ in range(2):
            for player in self.active_players:
                player.add_card(self.deck.draw_one())

    def _update_bank(self):
        """collect all bets after each stage"""
        for player in self.players:
            self.pot.add_chips(player, player.decision.size)
            player.new_stage()

    def _find_winners(self):
        """Determine the rating of players' combinations and the list of players having each of them"""
        if self._number_of_players_left == 1:
            winner = self.active_players[0]
            self.rating = [(None, [winner])]
        else:
            self._stage_index = 5

            # calculate each active player's combination
            players_combinations: dict[Player: tuple]
            players_combinations = {player: best_hand(player.hand + self.board) for player in self.active_players}
            # combine all present combinations to a set
            combs = {comb for _, comb in players_combinations.items()}
            # group players that have the same combination
            players_grouped_by_combinations: dict[Combination: list[Player]] = {comb: [] for comb in combs}
            for player, comb in players_combinations.items():
                players_grouped_by_combinations[comb].append(player)
            # sort players groups by their combinations and store it
            self.rating = sorted(players_grouped_by_combinations.items(), reverse=True)

    def _end(self):
        """Find winners and give them money"""
        self.pot.recalculate_pots()
        self._find_winners()
        self.pot.distribute(self.rating)
        self.pot.pay_wins()

        # todo replace print with log or view call
        self.print_winners()
        pp.pprint(self.get_status())
        print()
        for player in self.players:
            player.new_game_round()

    def print_winners(self):
        """Show players' hands if it's the showdown and highlight the winner"""
        # todo replace the whole method with log or view call
        if len(self.active_players) > 1:
            print("\nPlayers' hands:")
            pp.pprint({player: player.hand for player in self.active_players})
        print("\nRound rating:")
        pp.pprint(self.rating)
        print("\nPots distribution:")
        pp.pprint(self.pot.winners)
        print('\n')

    def get_status(self):
        """return current game stage, players statuses, the bank and the board"""
        return {
            'stage': self.STAGES[self._stage_index],
            'board': self.board,
            'pot': self.pot.pot_size,
            'players': [player.get_reduced_status() for player in self.players]
        }
