from functools import lru_cache
from typing import Iterable

from entities.cards import Suit, SUITS, Card, Value, VALUES, ZERO_ACE


class Combination:
    """
    Class for combinations and their comparison
    Combinations are initialized according to the tuple in the bottom part of the file
    Each combination has a priority to others and a function that defines if cards math the combination
    Combinations are comparable to each other by priority
    """

    def __init__(self, priority: int, func, name):
        self.priority: int = priority
        self.func = func
        self.name = name

    def check(self, cards) -> [tuple, None]:
        """Runs combination check function and passes its results"""
        return self.func(cards)

    def __gt__(self, other):
        return self.priority > other.priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        return self.priority == other.priority

    def __hash__(self):
        return hash(self.priority)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


@lru_cache(maxsize=128)
def duplicates(cards: Iterable[Card]) -> dict:
    """find how many duplicates are present in the known cards"""
    _duplicates = {}
    for value in VALUES:
        _duplicates[value] = len([card for card in cards if card.value == value])
    return _duplicates


def _card_ranges() -> list[tuple[Value]]:
    """all possible ranges for straights"""
    _values = (ZERO_ACE,) + VALUES
    return [tuple(_values[value_index] for value_index in range(i, i + 5)) for i in range(len(_values[:-4]))]


CARD_RANGES = _card_ranges()


def cards_in_ranges(cards: [list[Card], tuple[Card]]) -> dict[Value: int]:
    """Shows how many uniq cards values are present in each possible range"""
    _cards = list(cards)
    _cards_in_ranges = {}
    # duplicate aces for a-to-5 straights
    card_values_set = {c.value for c in _cards}
    if Value(14, 'Ace', 'A') in card_values_set:
        card_values_set.add(ZERO_ACE)
    # count uniq values of given cards for each straight range
    for _range in CARD_RANGES:
        _cards_in_ranges[_range] = len(set(_range).intersection(card_values_set))
    return _cards_in_ranges


def cards_by_suit(cards: [list[Card], tuple[Card]]) -> dict[Suit: int]:
    """Shows how many cards are present of each suit"""
    return {suit: len([card for card in cards if card.suit == suit]) for suit in SUITS}


def high_card(cards: Iterable[Card]) -> [None, tuple[Card, list[Card]]]:
    """
    Checks if there is at least one card.
    :param cards: an Iterable of Cards.
    :return: The highest card and the next up to 4 cards sorted by value descending
    """
    if not cards:
        return None
    _cards = sorted(cards, key=lambda c: c.value, reverse=True)
    return _cards[0], tuple(_cards[1:min(5, len(_cards))])


def pair(cards: Iterable[Card]) -> [None, tuple[Value, list[Card]]]:
    """
    Checks if there is exactly one pair in the hand
    Returns the value of the pair and top 3 cards by value
    """
    values = {card.value for card in cards}
    pair_values = []
    for value in values:
        if len([card for card in cards if card.value == value]) == 2:
            pair_values.append(value)
    if len(pair_values) == 1:
        return pair_values[0], tuple(sorted([card for card in cards if card.value != pair_values[0]],
                                            key=lambda c: c.value,
                                            reverse=True)[:3])

    return None


def two_pairs(cards: list[Card]) -> [None, tuple[Value, Value, Card]]:
    """
    Checks if there are at least two pairs in the hand
    Returns the values of the two pairs sorted by value and the highest of the rest cards
    """
    if len(cards) < 4:
        return None
    values = {card.value for card in cards}
    pair_values: list[Value] = []
    for value in values:
        if len([card for card in cards if card.value == value]) == 2:
            pair_values.append(value)
    pair_values.sort(reverse=True)
    if len(pair_values) >= 2:
        try:
            return pair_values[0], pair_values[1], max((card for card in cards if card.value not in pair_values[:2]),
                                                       key=lambda c: c.value)
        except ValueError:
            return pair_values[0], pair_values[1], None

    return None


def three_of_a_kind(cards: list[Card]) -> [None, tuple[Value, list[Card]]]:
    """
    Checks if there is exactly one three-of-a-kind in the hand
    Returns the value of the set and top a cards by value
    """
    if len(cards) < 3:
        return None
    values = {card.value for card in cards}
    set_values = []
    for value in values:
        if len([card for card in cards if card.value == value]) == 3:
            set_values.append(value)
    if len(set_values) == 1:
        return set_values[0], tuple(sorted([card for card in cards if card.value != set_values[0]],
                                           key=lambda c: c.value,
                                           reverse=True)[:2])
    return None


def _in_a_row(values: list[Value]) -> bool:
    """Technical function to help with straight"""
    return all(v.order + 1 == values[i + 1].order for i, v in enumerate(values[:-1]))


def straight(cards: list[Card]) -> [None, list[Value]]:
    """defines if player's hand is straight"""
    if len(cards) < 5:
        return None
    _cards = list(cards)
    # duplicate aces for a-to-5 straights
    for ace in (card for card in cards if card.value == Value(14, 'Ace', 'A')):
        _cards.append(Card(ace.suit, ZERO_ACE))
    # sort cards by values
    card_values = {c.value for c in _cards}
    if len(card_values) < 5:
        return None

    max_range = len(card_values) - 4
    sorted_cards_values = sorted(card_values)
    # try to find a sequence of sorted cards
    for i in list(range(0, max_range))[::-1]:
        current_range = sorted_cards_values[0 + i: 5 + i]
        if _in_a_row(current_range):
            return tuple(current_range[::-1])
    return None


def flush(cards: list[Card]) -> [None, tuple[Card]]:
    """
    defines if there is a flush in given cards
    returns the top 5 cards of the flush
    """
    if len(cards) < 5:
        return None
    for suit in SUITS:
        flush_cards = [card for card in cards if card.suit == suit]
        if len(flush_cards) >= 5:
            return tuple(sorted(flush_cards, key=lambda c: c.value, reverse=True)[:5])
    return None


def full_house(cards: list[Card]) -> [None, tuple[Value, Value]]:
    """
    Defines if there is a full house in given cards
    Returns the tuple of values of the set and the pair
    """
    if len(cards) < 5:
        return None
    values = {card.value for card in cards}
    pair_values: list[Value] = []
    set_values: list[Value] = []
    for value in values:
        if len([card for card in cards if card.value == value]) == 2:
            pair_values.append(value)
        elif len([card for card in cards if card.value == value]) == 3:
            set_values.append(value)
    pair_values.sort(reverse=True)

    if len(pair_values) >= 1 and len(set_values) == 1:
        return set_values[0], pair_values[0]

    if len(set_values) == 2:
        set_values.sort(reverse=True)
        return set_values[0], set_values[1]

    return None


def four_of_a_kind(cards: list[Card]) -> [None, tuple[Value, Value]]:
    """
    Defines if there is a four-of-a-kind in the given cards
    Returns the value of the four of a kind and the highest card of the rest
    """
    if len(cards) < 4:
        return None
    values = {card.value for card in cards}
    four_values: list[Value] = []
    for value in values:
        if len([card for card in cards if card.value == value]) == 4:
            four_values.append(value)
    if len(four_values) == 1:
        try:
            return four_values[0], max(card.value for card in cards if card.value not in four_values)  # noqa
        except ValueError:
            return four_values[0], None
    else:
        return None


def straight_flush(cards: list[Card]) -> [None, list[Card]]:
    """
    Defines if there is a straight flush in the given cards
    returns the values of the cards in the straight flush ordered by descending value
    """
    _cards = list(cards)
    # duplicate aces for a-to-5 straights
    for ace in (card for card in cards if card.value == Value(14, 'Ace', 'A')):
        _cards.append(Card(ace.suit, ZERO_ACE))
    # sort cards by values
    card_values = {c.value for c in _cards}
    if len(card_values) < 5:
        return None

    max_range = len(card_values) - 4
    sorted_cards_values = sorted(card_values)
    # try to find a sequence of sorted cards
    for i in list(range(0, max_range))[::-1]:
        current_range = sorted_cards_values[0 + i: 5 + i]
        range_cards = [card for card in _cards if card.value in current_range]
        if _in_a_row(current_range) and (f := flush(range_cards)):
            return f

    return None


def royal_flush(cards: list[Card]) -> [None, list[Card]]:
    """Defines if there is a royal flush in the given cards"""
    _straight_flush = straight_flush(cards)
    if _straight_flush and _straight_flush[0].value == Value(14, 'Ace', 'A'):
        return _straight_flush

    return None


COMBINATIONS = (  # do not reorder
    Combination(9, royal_flush, 'royal_flush'),
    Combination(8, straight_flush, 'straight_flush'),
    Combination(7, four_of_a_kind, 'four_of_a_kind'),
    Combination(6, full_house, 'full_house'),
    Combination(5, flush, 'flush'),
    Combination(4, straight, 'straight'),
    Combination(3, three_of_a_kind, 'three_of_a_kind'),
    Combination(2, two_pairs, 'two_pairs'),
    Combination(1, pair, 'pair'),
    Combination(0, high_card, 'high_card')
)


# @lru_cache(maxsize=128)
def best_hand(cards: Iterable[Card]) -> tuple[Combination, tuple]:
    """
    Defines the best hand that can be made from the given cards.
    Returns Combination class and the list of found cards to compare hands
    different hands can be "equal" if they have Combination of the same priority,
    and the same order of primary and secondary cards.
    """
    for combination in COMBINATIONS:
        found = combination.check(cards)
        if found:
            return combination, found
    raise RuntimeError("No best hand found")


if __name__ == '__main__':
    from cards import Deck

    print(*_card_ranges(), sep='\n')
    print(cards_in_ranges(list(Deck.all_cards())))
