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
    card_values_set = {c.value for c in cards}
    # duplicate aces for a-to-5 straights
    if Value(14, 'Ace', 'A') in card_values_set:
        card_values_set.add(ZERO_ACE)

    # count uniq values of given cards for each straight range
    _cards_in_ranges = {}
    for _range in CARD_RANGES:
        _cards_in_ranges[_range] = len(set(_range).intersection(card_values_set))

    return _cards_in_ranges


def cards_by_suit(cards: [list[Card], tuple[Card]]) -> dict[Suit: int]:
    """Shows how many cards are present of each suit"""
    return {suit: len([card for card in cards if card.suit == suit]) for suit in SUITS}


def high_card(cards: Iterable[Card]) -> [None, tuple[Value, list[Value]]]:
    """
    Checks if there is at least one card.
    :param cards: an Iterable of Cards.
    :return: The highest card and the next up to 4 cards sorted by value descending
    """
    if not cards:
        return None
    _cards = sorted(cards, key=lambda c: c.value, reverse=True)
    return _cards[0].value, tuple(card.value for card in _cards[1:min(5, len(_cards))])


def pair(cards: Iterable[Card]) -> [None, tuple[Value, list[Value]]]:
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
        return pair_values[0], tuple(sorted([card.value for card in cards if card.value != pair_values[0]],  # noqa
                                            reverse=True)[:3])

    return None


def two_pairs(cards: list[Card]) -> [None, tuple[Value, Value, [Value, None]]]:
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
            return pair_values[0], pair_values[1], max((card.value for card in cards if card.value not in pair_values[:2]))  # noqa
        except ValueError:
            return pair_values[0], pair_values[1], None

    return None


def three_of_a_kind(cards: list[Card]) -> [None, tuple[Value, list[Value]]]:
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
        return set_values[0], tuple(sorted((card.value for card in cards if card.value != set_values[0]),  # noqa
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
        flush_cards = [card.value for card in cards if card.suit == suit]
        if len(flush_cards) >= 5:
            return tuple(sorted(flush_cards, reverse=True)[:5])  # noqa
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


def straight_flush(cards: list[Card]) -> [None, list[Value]]:
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
    if _straight_flush and _straight_flush[0] == Value(14, 'Ace', 'A'):
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


VALUE_BY_ORDER = {value.order: value for value in VALUES}


def _straight_from_values(card_values: set[Value]) -> [None, tuple[Value, ...]]:
    """Find the highest straight from a set of card values."""
    orders = {value.order for value in card_values}
    if 14 in orders:
        orders.add(1)

    for high in range(14, 4, -1):
        straight_orders = range(high, high - 5, -1)
        if all(order in orders for order in straight_orders):
            return tuple(ZERO_ACE if order == 1 else VALUE_BY_ORDER[order] for order in straight_orders)
    return None


def best_hand(cards: Iterable[Card]) -> tuple[Combination, tuple]:
    """
    Defines the best hand that can be made from the given cards.
    Returns Combination class and the list of found cards to compare hands
    different hands can be "equal" if they have Combination of the same priority,
    and the same order of primary and secondary cards.
    """
    cards = tuple(cards)
    if not cards:
        raise RuntimeError("No cards provided")

    value_counts: dict[Value, int] = {}
    suit_values: dict[Suit, list[Value]] = {}
    values_desc: list[Value] = []
    unique_values: set[Value] = set()
    for card in cards:
        value = card.value
        suit = card.suit
        value_counts[value] = value_counts.get(value, 0) + 1
        suit_values.setdefault(suit, []).append(value)
        values_desc.append(value)
        unique_values.add(value)

    values_desc.sort(reverse=True)

    straight_flush_found = None
    for suit in SUITS:
        flush_values = suit_values.get(suit)
        if not flush_values or len(flush_values) < 5:
            continue
        straight_flush_found = _straight_from_values(set(flush_values))
        if straight_flush_found:
            if straight_flush_found[0] == VALUE_BY_ORDER[14]:
                return COMBINATIONS[0], straight_flush_found
            return COMBINATIONS[1], straight_flush_found

    groups_by_count: dict[int, list[Value]] = {}
    for value, count in value_counts.items():
        groups_by_count.setdefault(count, []).append(value)
    for values in groups_by_count.values():
        values.sort(reverse=True)

    fours = groups_by_count.get(4, [])
    if fours:
        quad = fours[0]
        kicker = max((value for value in values_desc if value != quad), default=None)
        return COMBINATIONS[2], (quad, kicker)

    trips = groups_by_count.get(3, [])
    pairs = groups_by_count.get(2, [])
    if trips:
        if pairs:
            return COMBINATIONS[3], (trips[0], pairs[0])
        if len(trips) >= 2:
            return COMBINATIONS[3], (trips[0], trips[1])

    for suit in SUITS:
        flush_values = suit_values.get(suit)
        if flush_values and len(flush_values) >= 5:
            return COMBINATIONS[4], tuple(sorted(flush_values, reverse=True)[:5])

    straight_found = _straight_from_values(unique_values)
    if straight_found:
        return COMBINATIONS[5], straight_found

    if trips:
        trip = trips[0]
        kickers = tuple(value for value in values_desc if value != trip)[:2]
        return COMBINATIONS[6], (trip, kickers)

    if len(pairs) >= 2:
        high_pair, low_pair = pairs[:2]
        kicker = next((value for value in values_desc if value not in (high_pair, low_pair)), None)
        return COMBINATIONS[7], (high_pair, low_pair, kicker)

    if len(pairs) == 1:
        pair_value = pairs[0]
        kickers = tuple(value for value in values_desc if value != pair_value)[:3]
        return COMBINATIONS[8], (pair_value, kickers)

    return COMBINATIONS[9], (values_desc[0], tuple(values_desc[1:min(5, len(values_desc))]))
