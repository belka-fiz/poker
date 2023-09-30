from typing import Union

from common.event import post_event, EventType
from entities.bet_processor import BetProcessor
from entities.cards import Card, Deck
from entities.combinations import Combination, best_hand
from entities.players import Player
from entities.pot import Pot


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
        self.players: list[Union[Player]] = players[dealer_index + 1:] + players[:dealer_index + 1]
        self.blind_size = blind_size
        self.debug = debug

        self.deck = Deck()
        self._board: list[Card] = []
        self.stage_index = 0
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
        self.stage_index += 1
        self._deal_board(self.NUMBER_OF_CARDS[self.stage_index])

        post_event(EventType.NEW_STAGE, self.board, self.pot)

        # post blinds if pre-flop
        if self.stage_index == 1:
            for i, player in enumerate(self.active_players[:2]):
                amount = self.blind_size / 2 * (1 + i)
                player.status.post_blind(amount)
                post_event(EventType.PLAYER_MOVED, player)
            if not self.debug:
                self._bets_round(self.players[1])
        elif not self.debug:
            self._bets_round()

        if not self.debug:
            # find winners if necessary or proceed to the next stage
            if self._number_of_players_left == 1 or self.stage_index == 4:
                self._end()
            else:
                self.new_stage()

    @property
    def active_players(self) -> list[Player]:
        """Provides the list of players who haven't folded"""
        return [player for player in self.players if player.status.is_active]

    def players_to_move(self) -> list[Player]:
        """List of players yet to move"""
        return [player for player in self.players if player.status.yet_to_move(self.max_bet)]

    @property
    def _number_of_players_left(self):
        """Number of players left in the game(not folded)"""
        return len(self.active_players)

    @property
    def max_bet(self):
        """The size of the biggest bet in the current game stage"""
        return max(player.status.last_move.size for player in self.players)

    def players_to_move_since_last_raiser(self, last_raiser: Player) -> list[Player]:
        """make a queue of players to move after the last raiser"""
        try:
            index = self.players_to_move().index(last_raiser)
        except ValueError:
            index = -1
        return self.players_to_move()[index + 1:] + self.players_to_move()[:index + 1]

    def _bets_round(self, last_raiser: [Player] = None):
        """cycle through active players and get players' moves"""
        # reset each player's decision except the last raiser and the ones who are all-in
        for player in self.active_players:
            if player is not last_raiser:
                player.status.reset_soft()

        # cycle through players and ask for a decision
        for player in self.players_to_move_since_last_raiser(last_raiser):
            current_max_bet = self.max_bet
            if player.is_ai:
                with AIBetProcessor(player, current_max_bet) as bet_processor:
                    post_event(EventType.PLAYER_MAKE_MOVE, bet_processor, self)
            else:
                with BetProcessor(player, current_max_bet) as bet_processor:
                    post_event(EventType.PLAYER_MAKE_MOVE, bet_processor, self)
            post_event(EventType.PLAYER_MOVED, player)

            if player.status.last_move.size > current_max_bet:
                last_raiser = player
                self._bets_round(last_raiser)
                return
        self._update_bank()

    def deal_players_cards(self):
        """just deal cards starting from the next after dealer"""
        for player in self.players:
            player.reset()
        for _ in range(2):
            for player in self.active_players:
                player.add_card(self.deck.draw_one())

    def _update_bank(self):
        """collect all bets after each stage"""
        for player in self.players:
            self.pot.add_chips(player, player.status.last_move.size)
            player.status.reset_soft()

    def _find_winners(self):
        """Determine the rating of players' combinations and the list of players having each of them"""
        if self._number_of_players_left == 1:
            winner = self.active_players[0]
            self.rating = [(None, [winner])]
        else:
            self.stage_index = 5

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

        post_event(EventType.WINNERS_CALCULATED, self)
        post_event(EventType.ROUND_END, self)

        for player in self.players:
            player.reset()

    def end_stats(self):
        """Game stage closing stats: the stage, the board and the players' end stack"""
        return {
            'stage': self.STAGES[self.stage_index],
            'board': self.board,
            'players': [{player.NAME: player.status.stack} for player in self.players]
        }

    def get_status(self):
        """return current game stage, players statuses, the bank and the board"""
        return {
            'stage': self.STAGES[self.stage_index],
            'board': self.board,
            'pot': self.pot.pot_size,
            'players': [player.status.get() for player in self.players]
        }
