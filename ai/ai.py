"""
1) Define opponents' probability of each combination on the table accroding to Cards on the table and in the hand
    - On river
    - On turn
    - On flop ?
2) Decide to bet or not according to the probabilities(check/fold, check/call, call/raise, all-in)
3) Try to guess opponents' hands by their bets
"""
from functools import lru_cache
from secrets import SystemRandom

from cards import Card, Deck, VALUES
from combinations import best_hand, Combination, COMBINATIONS
from config import WEIGHT_QUOTIENT
from players import Player


random = SystemRandom()


@lru_cache(128)
def all_possible_sets_to_open(
        known_cards: [tuple[Card], set[Card]],
        for_competitor=False
) -> set[frozenset[Card]]:
    """find all cards that can be possibly opened later or found in competitor's hand"""
    result: set[frozenset[Card]] = set()
    deck_rest = Deck.all_cards() - set(known_cards)
    number_of_cards_to_open = 7 - len(known_cards) + (2 * for_competitor)
    if number_of_cards_to_open == 0:
        return result
    elif number_of_cards_to_open == 1:
        return set(frozenset([card]) for card in deck_rest)
    else:
        for card in deck_rest:
            for _result in all_possible_sets_to_open(known_cards + tuple([card]), for_competitor=for_competitor):
                intermediate_inner_result = _result | {card}
                result.add(intermediate_inner_result)
    return result


@lru_cache(128)
def possible_boards(board: tuple[Card]) -> set[frozenset[Card]]:
    deck_rest = Deck.all_cards() - set(board)
    if len(board) == 5:
        return set()
    elif 5 - len(board) == 1:
        return set(frozenset([card]) for card in deck_rest)
    else:
        result: set[frozenset[Card]] = set()
        for card in deck_rest:
            for _result in possible_boards(board + tuple([card])):
                result.add(_result | {card})
    return result


def possible_board_according_to_hand(board: tuple[Card], hand: tuple[Card]) -> set[frozenset[Card]]:
    possible_rest = possible_boards(board)
    result = possible_rest.copy()
    for _result in possible_rest:
        for card in hand:
            if card in _result:
                result.discard(_result)
                break
    return result


def possible_competitors_sets(board: tuple[Card], hand: tuple[Card]) -> set[frozenset[Card]]:
    possible_rest = possible_board_according_to_hand(board, hand)
    result = possible_rest.copy()
    # todo add possible hands
    return result


def update_smallest(chances: dict[Combination: float]) -> None:
    """find the smallest combination with >0 chance and set its chances to 1"""
    for cmb in chances:
        smaller_cmbs = COMBINATIONS[COMBINATIONS.index(cmb)+1:]
        if len(smaller_cmbs) == 0:
            return
        elif max(chances[smaller_cmb] for smaller_cmb in smaller_cmbs) == 0 and chances[cmb] > 0:
            chances[cmb] = 1.0
            break


@lru_cache(128)
class StageBetAI:
    def __init__(self, board: tuple[Card], player: Player, blind: float, players_left: int):
        self.player = player
        self.board = board
        self.hand = tuple(player.hand)
        self.known_cards = self.hand + board
        self.blind = blind
        self.players_left = players_left
        self.possible_left_cards = possible_board_according_to_hand(board, self.hand)
        self.possible_competitors_cards = all_possible_sets_to_open(self.known_cards, True)
        self.possible_variations = len(self.possible_left_cards) or 1
        self.possible_competitors_variations = len(self.possible_competitors_cards)
        self.my_chances = self._guess_my_chances()
        self.competitors_chances = self._guess_opponents_chances()
        self.my_weight = sum(self.my_chances[cmb] * (WEIGHT_QUOTIENT ** cmb.priority) for cmb in COMBINATIONS)
        self.competitors_weight = sum(
            self.competitors_chances[cmb] * (WEIGHT_QUOTIENT ** cmb.priority) for cmb in COMBINATIONS)
        self.weight_ratio = self.my_weight / self.competitors_weight
        self.bluff: bool = False

    def _guess_my_chances(self) -> dict[Combination: float]:
        # todo add combination's kicker
        absolute_chances = {cmb: 0 for cmb in COMBINATIONS}
        if len(self.known_cards) == 7:
            absolute_chances.update({best_hand(self.known_cards)[0]: 1})
            return absolute_chances
        else:
            for possible_card_set in self.possible_left_cards:
                possible_hand = self.known_cards + tuple(possible_card_set)
                absolute_chances[best_hand(possible_hand)[0]] += 1
            relative_chances = {k: v / self.possible_variations for k, v in absolute_chances.items()}
            update_smallest(relative_chances)
            return relative_chances

    def _guess_opponents_chances(self) -> dict[Combination: float]:
        # todo add combination's kicker
        absolute_chances = {cmb: 0 for cmb in COMBINATIONS}
        for possible_card_set in self.possible_competitors_cards:
            possible_hand = self.board + tuple(possible_card_set)
            absolute_chances[best_hand(possible_hand)[0]] += 1
        relative_chances = {k: (v / self.possible_competitors_variations) for k, v in absolute_chances.items()}
        update_smallest(relative_chances)
        return relative_chances

    @lru_cache(128)
    def will_i_win_by_weight(self):
        if self.weight_ratio > 1:
            return True
        elif self.weight_ratio < 0.79:
            if self.competitors_weight < 5 and random.randint(0, 100) > 60:
                self.bluff = True
                return True
            else:
                return False
        else:
            return None

    def comfort_bet(self) -> float:
        if self.bluff:
            return random.randint(1, 3) * self.blind
        return round(self.weight_ratio ** 2) * self.blind

    def should_i_bet(self, max_bet) -> list[str]:
        if self.comfort_bet() * 3 < max_bet:
            return ['fold']
        elif self.will_i_win_by_weight() is True or self.bluff:
            return ['raise', 'call', 'all_in']
        elif self.will_i_win_by_weight() is False:
            return ['check', 'fold']
        elif self.will_i_win_by_weight() is None:
            return ['check', 'call', 'fold']

    def how_much_to_bet(self, max_bet) -> float:
        bet = self.comfort_bet() * random.randint(0, 3)
        return min(max(bet, max_bet), self.player.stack)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self


class PreFlopDecider:
    def __init__(self, player: Player):
        self.player = player
        self.__hand = player.hand
        self._weight = self.weight()

    def is_pair(self) -> bool:
        return self.__hand[0].value == self.__hand[1].value

    def dist_quotient(self) -> float:
        distance = abs(self.__hand[0].value.order - self.__hand[1].value.order)
        return 1 - min(distance, 4) / 20

    def suit_quotient(self) -> float:
        same_suit = self.__hand[0].suit == self.__hand[1].suit
        return 0.8 + 0.2 * same_suit

    def highness(self) -> float:
        return max(self.__hand).value.order / max(VALUES).order

    def weight(self) -> float:
        if self.is_pair():
            return self.highness()
        else:
            return 0.8 * self.highness() * self.dist_quotient() * self.suit_quotient()

    def decision(self) -> list[str]:
        # print(f"Deciding about preflop. Hand: {self.__hand}, weight: {self._weight:.3f}")
        if self._weight > 0.7:
            return ['raise', 'call', 'all_in']
        elif 0.7 >= self._weight >= 0.4:
            return ['raise', 'check', 'call', 'fold']
        else:
            return ['check', 'fold']

    def how_much_to_bet(self, blind, current_bet):
        if self._weight > 0.8:
            bet = 3 * blind
        elif self._weight > 0.6:
            bet = 2 * blind
        else:
            bet = blind
        return min([max([bet, current_bet]), self.player.get_bet + self.player.stack])


# class AI(Player):
#     def __init__(self, start_stack: float, pre_flop_agression: float, stage_agression: float):
#         super().__init__(start_stack)
def possible_competitors_hands(known_cards: tuple[Card] = None) -> set[frozenset[Card]]:
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