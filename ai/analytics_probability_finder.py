from functools import cached_property
from typing import Collection

from entities.cards import Card, Deck, SUITS, VALUES, Value, Suit, ZERO_ACE
from entities.combinations import best_hand, duplicates, cards_by_suit, cards_in_ranges, CARD_RANGES

"""
- Find probability of having on an opponent's hand, according to known cards:
    - Pair
    - Exact pair
    - Exact not pair cards
    - Higher than we have
    - Suited cards
    - Connectors
    - Suited connectors?
    - Connectors with a hole?
- if a combination already present on the board:
    - for each combination
- Find if a combination is possible for:
    - straight
    - flush
    - full house
    - four of a kind
    - straight flush
"""


class ProbabilityCounter:
    """
    Class aimed to find win chances using combinatorincs and not just simply guessing all possible cards
    Calculate chances of duplicates, suit matches, cards amount in different ranges, etc
    """

    def __init__(self, pocket_cards: Collection[Card], community_cards: Collection[Card] = None):
        self.hand = tuple(pocket_cards)
        self.board = tuple(community_cards or [])
        self.known_cards = self.hand + self.board
        self.cards_left = 52 - len(self.known_cards)
        self.my_combination = best_hand(self.known_cards)

    @cached_property
    def duplicates_in_known(self) -> dict:
        """find how many dulpicates are present in the known cards"""
        return duplicates(self.known_cards)

    @cached_property
    def duplicates_on_board(self) -> dict:
        """find how many dulpicates are present on the board"""
        return duplicates(self.board)

    @cached_property
    def suited_count_in_known(self) -> dict:
        """shows how many suited cards are present in the known cards"""
        return cards_by_suit(self.known_cards)

    @cached_property
    def suited_count_on_board(self) -> dict:
        """shows how many suited cards are present in the known community cards"""
        return cards_by_suit(self.board)

    @cached_property
    def board_cards_by_range(self) -> dict:
        """Shows how many cards in each range there are on the board"""
        return cards_in_ranges(self.board)

    @cached_property
    def known_cards_by_range(self) -> dict:
        """Shows how many cards in each range there are in the known cards"""
        return cards_in_ranges(self.known_cards)

    @cached_property
    def pocket_one_card_probability(self) -> dict:
        """Shows the probability of getting a card of each value from deck"""
        return {value: (4 - self.duplicates_in_known[value])/self.cards_left for value in VALUES}

    @cached_property
    def pocket_at_least_one_card_probability(self) -> dict:
        """find the probability that an opponent have a card of the exact value"""
        card_probability = {}
        for value in VALUES:
            single_probability = (4 - self.duplicates_in_known[value]) / self.cards_left
            second_card_probability = (4 - self.duplicates_in_known[value]) / (self.cards_left - 1)
            card_probability[value] = single_probability + (1 - single_probability) * second_card_probability
        # card_probability = {value: (4 - self.duplicates_in_known[value])/self.cards_left for value in VALUES}
        return card_probability

    @cached_property
    def pocket_pair_probability(self) -> dict:
        """Shows the probability of getting a pair of each value"""
        pair_probability = {}
        for value in VALUES:
            count = self.duplicates_in_known[value]
            if count > 2:
                pair_probability[value] = 0
            else:
                pair_probability[value] = (4 - count) / self.cards_left * (3 - count) / (self.cards_left - 1)
        return pair_probability

    @cached_property
    def pocket_suit_probability(self) -> dict:
        """Probabilities that an opponent gets at least one card for each suit"""
        return {suit: (13 - self.suited_count_in_known[suit]) / self.cards_left for suit in SUITS}

    def several_cards_probability_by_value(self, values: [list[Value], tuple[Value]]) -> float:
        """Probability of getting several cards with exact values"""
        _cards_left = self.cards_left
        probability = 1
        for value in values:
            if value is ZERO_ACE:
                _value = VALUES[-1]
            else:
                _value = value
            probability *= (4 - self.duplicates_in_known[_value]) / _cards_left
            _cards_left -= 1
        return probability

    def several_cards_probability_by_suit(self, suit: Suit, count: int) -> float:
        """Probability of getting several cards of the exact suit"""
        _cards_left = self.cards_left
        _suit_cards_used = self.suited_count_in_known[suit]
        probability = 1
        for _ in range(count):
            probability *= (13 - _suit_cards_used) / _cards_left
            _cards_left -= 1
            _suit_cards_used += 1
        return probability

    def pocket_suited_cards_probability(self) -> dict:
        """Probability that an opponent has suited cards"""
        suit_probability = {}
        for suit in SUITS:
            suit_count = self.suited_count_in_known[suit]
            suit_probability[suit] = (13 - suit_count) / self.cards_left * (12 - suit_count) / (self.cards_left - 1)
        return suit_probability

    def straight_possibilities(self) -> dict:
        """probabilities of getting the straight for each range"""
        _straight_possibilities = {}
        for _range in CARD_RANGES:
            if (5 - self.board_cards_by_range[_range]) <= 2 + (5 - len(self.board)):
                left_cards = [value for value in _range if value not in [card.value for card in self.board]]
                _straight_possibilities[_range] = self.several_cards_probability_by_value(left_cards)
            else:
                _straight_possibilities[_range] = 0
        return _straight_possibilities

    def flush_possibilities(self) -> dict:
        """Probabilities to get flush for each suit"""
        _flush_possibilities = {}
        for suit in SUITS:
            cards_left = (5 - self.suited_count_on_board[suit])
            if cards_left <= 2 + (5 - len(self.board)):
                _flush_possibilities[suit] = self.several_cards_probability_by_suit(suit, cards_left)
            else:
                _flush_possibilities[suit] = 0
        return _flush_possibilities


if __name__ == '__main__':
    deck = Deck()
    hand = tuple(deck.draw_one() for _ in range(2))
    print(f"My hand is {hand}")
    board = tuple(deck.draw_one() for _ in range(3))
    print(f"The board is {board}")
    board_counter = ProbabilityCounter(hand, board)
    print(board_counter.pocket_at_least_one_card_probability)
    print(board_counter.pocket_pair_probability)
    print(board_counter.pocket_suit_probability)
    print(board_counter.pocket_suited_cards_probability())
    print(board_counter.straight_possibilities())
    print(sum(board_counter.straight_possibilities().values()))
    print(board_counter.flush_possibilities())
    print(sum(board_counter.flush_possibilities().values()))
    print(best_hand(hand + board))
