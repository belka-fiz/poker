"""
1) Define opponents' probability of each combination on the table accroding to Cards on the table and in the hand
    - On river
    - On turn
    - On flop ?
2) Decide to bet or not according to the probabilities(check/fold, check/call, call/raise, all-in)
3) Try to guess opponents' hands by their bets
"""
from functools import lru_cache
from itertools import combinations
from math import comb
from secrets import SystemRandom

from common.config import WEIGHT_QUOTIENT
from common.event import EventType, subscribe
from entities.bet import Bet, Decision
from entities.cards import Card, Deck, VALUES
from entities.combinations import best_hand, Combination, COMBINATIONS
from entities.players import Player
from entities.round import Round
from errors.errors import UnavailableDecision, TooSmallBetError

random = SystemRandom()
FULL_DECK = frozenset(Deck.all_cards())
UNSET = object()


@lru_cache(128)
def possible_boards(board: tuple[Card]) -> set[frozenset[Card]]:
    """Find all cards that can complete the board if we wouldn't know our own pocket cards"""
    number_of_cards_to_open = 5 - len(board)
    if number_of_cards_to_open <= 0:
        return set()

    deck_rest = FULL_DECK.difference(board)
    return {frozenset(card_set) for card_set in combinations(deck_rest, number_of_cards_to_open)}


@lru_cache(128)
def possible_board_according_to_hand(board: tuple[Card], hand: tuple[Card]) -> set[frozenset[Card]]:
    """All possible boards knowing own hand"""
    hand_cards = frozenset(hand)
    return {_result for _result in possible_boards(board) if _result.isdisjoint(hand_cards)}


def possible_competitors_sets(board: tuple[Card], hand: tuple[Card]) -> set[frozenset[Card]]:
    """All possible competitors hands(TBC)"""
    possible_rest = possible_board_according_to_hand(board, hand)
    result = possible_rest.copy()
    # todo add possible hands
    return result


def update_smallest(chances: dict[Combination: float]) -> None:
    """find the smallest combination with >0 chance and set its chances to 1"""
    for cmb in chances:
        smaller_cmbs = COMBINATIONS[COMBINATIONS.index(cmb) + 1:]
        if len(smaller_cmbs) == 0:
            return

        if max(chances[smaller_cmb] for smaller_cmb in smaller_cmbs) == 0 and chances[cmb] > 0:
            chances[cmb] = 1.0
            break


class StageBetAI:
    """
    Bet decider for AI in the middle of the game
    Calculates all possible community cards and all possible opponent's pocket cards,
    then calculates the chances for each combination and multiplies if by weight of the combination.
    Decides if AI should bet or not and how much according to the weight ration of possible own and opponent's hands.
    Has a chance of bluff.
    """

    def __init__(self, board: tuple[Card], player: Player, blind: float, players_left: int):
        self.player = player
        self.board = board
        self.hand = tuple(player.hand)
        self.known_cards = self.hand + board
        self.blind = blind
        self.players_left = players_left
        self.possible_variations = self._possible_board_variations() or 1
        self.possible_competitors_variations = self._possible_competitor_variations() or 1
        self.my_chances = self._guess_my_chances()
        self.competitors_chances = self._guess_opponents_chances()
        self.my_weight = sum(self.my_chances[cmb] * (WEIGHT_QUOTIENT ** cmb.priority) for cmb in COMBINATIONS)
        self.competitors_weight = sum(
            self.competitors_chances[cmb] * (WEIGHT_QUOTIENT ** cmb.priority) for cmb in COMBINATIONS)
        self.weight_ratio = self.my_weight / self.competitors_weight
        self.bluff: bool = False
        self._will_i_win_by_weight = UNSET

    def _iter_possible_board_cards(self):
        cards_left_to_open = 5 - len(self.board)
        if cards_left_to_open <= 0:
            return

        deck_rest = FULL_DECK.difference(self.known_cards)
        for card_set in combinations(deck_rest, cards_left_to_open):
            yield card_set

    def _iter_possible_competitor_cards(self):
        cards_to_draw = 7 - len(self.known_cards) + 2
        if cards_to_draw <= 0:
            return

        deck_rest = FULL_DECK.difference(self.known_cards)
        for card_set in combinations(deck_rest, cards_to_draw):
            yield card_set

    def _possible_board_variations(self) -> int:
        cards_left_to_open = 5 - len(self.board)
        if cards_left_to_open <= 0:
            return 0
        return comb(len(FULL_DECK) - len(self.known_cards), cards_left_to_open)

    def _possible_competitor_variations(self) -> int:
        cards_to_draw = 7 - len(self.known_cards) + 2
        if cards_to_draw <= 0:
            return 0
        return comb(len(FULL_DECK) - len(self.known_cards), cards_to_draw)

    def _guess_my_chances(self) -> dict[Combination: float]:
        """Chances of getting each combination"""
        # todo add combination's kicker
        absolute_chances = {cmb: 0 for cmb in COMBINATIONS}
        if len(self.known_cards) == 7:
            absolute_chances.update({best_hand(self.known_cards)[0]: 1})
            return absolute_chances

        for possible_card_set in self._iter_possible_board_cards():
            possible_hand = self.known_cards + tuple(possible_card_set)
            absolute_chances[best_hand(possible_hand)[0]] += 1
        relative_chances = {k: v / self.possible_variations for k, v in absolute_chances.items()}
        update_smallest(relative_chances)
        return relative_chances

    def _guess_opponents_chances(self) -> dict[Combination: float]:
        """Chances for an opponent to get each combination"""
        # todo add combination's kicker
        absolute_chances = {cmb: 0 for cmb in COMBINATIONS}
        for possible_card_set in self._iter_possible_competitor_cards():
            possible_hand = self.board + tuple(possible_card_set)
            absolute_chances[best_hand(possible_hand)[0]] += 1
        relative_chances = {k: (v / self.possible_competitors_variations) for k, v in absolute_chances.items()}
        update_smallest(relative_chances)
        return relative_chances

    def will_i_win_by_weight(self):
        """
        Our assumption if we are winning or not
        True if we have good chances(or bluffing)
        False if chances are pretty bad
        None if we are not sure
        """
        if self._will_i_win_by_weight is not UNSET:
            return self._will_i_win_by_weight

        if self.weight_ratio > 1:
            self._will_i_win_by_weight = True
            return self._will_i_win_by_weight

        if self.weight_ratio < 0.79:
            if self.competitors_weight < 5 and random.randint(0, 100) > 60:
                self.bluff = True
                self._will_i_win_by_weight = True
                return self._will_i_win_by_weight
            self._will_i_win_by_weight = False
            return self._will_i_win_by_weight

        self._will_i_win_by_weight = None
        return self._will_i_win_by_weight

    def comfort_bet(self) -> float:
        """Defining the bet we are ready to call or raise"""
        if self.bluff:
            return random.randint(1, 3) * self.blind
        return round(self.weight_ratio ** 2) * self.blind

    def should_i_bet(self, max_bet) -> list[Bet]:
        """
        Defining what action we are ready to perform according to:
        - Our comfortable bet and the current max bet
        - Our guess about the chances to win
        """
        if self.comfort_bet() * 3 < max_bet:
            return [Bet.FOLD]

        if self.will_i_win_by_weight() is True or self.bluff:
            return [Bet.RAISE, Bet.CALL, Bet.ALL_IN]

        if self.will_i_win_by_weight() is False:
            return [Bet.CHECK, Bet.FOLD]

        if self.will_i_win_by_weight() is None:
            return [Bet.CHECK, Bet.CALL, Bet.FOLD]

        return []

    def how_much_to_bet(self, max_bet) -> float:
        """Deciding about the size of the raise using random"""
        bet = self.comfort_bet() * random.randint(0, 3)
        max_total_bet = self.player.decision.size + self.player.stack
        return min(max(bet, max_bet), max_total_bet)


class PreFlopDecider:
    """
    Decides if AI should bet on pre-flop depending on
    - if own pocket cards are pair
    - the values of the pocket cards
    """

    def __init__(self, player: Player):
        self.player = player
        self.__hand = player.hand
        self._weight = self.weight()

    def is_pair(self) -> bool:
        """if we have a pocket pair"""
        return self.__hand[0].value == self.__hand[1].value

    def dist_quotient(self) -> float:
        """How far the pocket cards are from each other"""
        distance = abs(self.__hand[0].value.order - self.__hand[1].value.order)
        return 1 - min(distance, 4) / 20

    def suit_quotient(self) -> float:
        """Are the pocket cards suited"""
        same_suit = self.__hand[0].suit == self.__hand[1].suit
        return 0.8 + 0.2 * same_suit

    def highness(self) -> float:
        """quotient for the highness of the pocket cards"""
        return max(self.__hand).value.order / max(VALUES).order

    def weight(self) -> float:
        """The overall weight of the pocket cards according to the quotients above"""
        if self.is_pair():
            return self.highness()

        return 0.8 * self.highness() * self.dist_quotient() * self.suit_quotient()

    def decision(self) -> list[Bet]:
        """Preffered actions according to the weight"""
        if self._weight > 0.7:
            return [Bet.RAISE, Bet.CALL, Bet.ALL_IN]

        if 0.7 >= self._weight >= 0.4:
            return [Bet.RAISE, Bet.CHECK, Bet.CALL, Bet.FOLD]

        return [Bet.CHECK, Bet.FOLD]

    def how_much_to_bet(self, blind, current_bet):
        """The size of the bet according to the weight"""
        if self._weight > 0.8:
            bet = 3 * blind
        elif self._weight > 0.6:
            bet = 2 * blind
        else:
            bet = blind
        return min([max([bet, current_bet]), self.player.decision.size + self.player.stack])


class AI(Player):
    """
    AI extention for Player's class
    Contains logic for calling bet decisions classes according to the stage of the game
    """

    def __init__(self,
                 start_stack: float,
                 name: str = '',
                 # pre_flop_agression: float = 0,
                 # stage_agression: float = 0
                 ):
        super().__init__(start_stack, is_ai=True, name=name)
        self._stage_ai_key = None
        self._stage_ai_cache = None

    def _current_stage_ai_key(self, board, blind_size, number_of_players_left):
        """Build a cache key for stage-level AI decisions."""
        return tuple(self.hand), tuple(board), blind_size, number_of_players_left

    def _get_stage_decider(self, board, blind_size, number_of_players_left):
        """Reuse the current stage decider while the stage state is unchanged."""
        key = self._current_stage_ai_key(board, blind_size, number_of_players_left)
        if self._stage_ai_key != key:
            self._stage_ai_key = key
            self._stage_ai_cache = StageBetAI(tuple(board), self, blind_size, number_of_players_left)
        return self._stage_ai_cache

    def reset_stage_ai_cache(self):
        """Drop stage-local AI state as soon as it is no longer useful."""
        self._stage_ai_key = None
        self._stage_ai_cache = None

    def new_stage(self):
        """Reset player state and release stage-level AI calculations."""
        super().new_stage()
        self.reset_stage_ai_cache()

    def new_game_round(self):
        """Reset round state and release any cached AI decider."""
        super().new_game_round()
        self.reset_stage_ai_cache()

    def make_a_move(self, board, current_max_bet, stage_index, blind_size, number_of_players_left):
        """Calling the logic for bet decisions"""
        if stage_index == 1:
            decider = PreFlopDecider(self)
            ai_decisions = decider.decision()
            try:
                action = [d for d in ai_decisions if d in self.available_actions][0]
            except IndexError:
                print("Something went wrong")
                print(f"Player's available decisions: {self.available_actions}")
                print(f"AI's suggested decisions: {ai_decisions}")
                raise UnavailableDecision
            amount = decider.how_much_to_bet(blind_size, current_max_bet)
            try:
                self.decide(Decision(action, amount))
            except TooSmallBetError as e:
                print(f"{current_max_bet=}, {self.stack=}, "
                      f"{self.requested_bet=}, {self.available_actions=}, "
                      f"{self.decision.size=}, {action=}, {amount=}")
                raise e
        else:
            decider = self._get_stage_decider(board, blind_size, number_of_players_left)
            ai_decisions = decider.should_i_bet(current_max_bet)
            try:
                action = [d for d in ai_decisions if d in self.available_actions][0]
            except IndexError:
                print("Something went wrong")
                print(f"Player's available decisions: {self.available_actions}")
                print(f"AI's suggested decisions: {ai_decisions}")
                raise UnavailableDecision
            self.decide(Decision(action, decider.how_much_to_bet(current_max_bet)))

    def make_a_move_by_round(self, game_round: Round):
        """adapter method for calling make a move providing round as a parameter"""
        if self.is_ai:
            self.make_a_move(
                game_round.board,
                self.requested_bet,
                game_round.stage_index,
                game_round.blind_size,
                len(game_round.active_players)
            )


def possible_competitors_hands(known_cards: tuple[Card] = None) -> set[frozenset[Card]]:
    """all possible pocket cards can be found at a competitor's"""
    cards = Deck.all_cards()
    if known_cards:
        for card in known_cards:
            cards.discard(card)
    result = set()
    for card in cards:
        for second_card in cards:
            if card is not second_card:
                result.add(frozenset([card, second_card]))
    return result


def clear_ai_caches(*args, **kwargs):
    """Release cached AI helper data when a stage or round is over."""
    possible_boards.cache_clear()
    possible_board_according_to_hand.cache_clear()


subscribe(EventType.NEW_STAGE, clear_ai_caches)
subscribe(EventType.ROUND_END, clear_ai_caches)
subscribe(EventType.PLAYER_MAKE_MOVE, AI.make_a_move_by_round)
