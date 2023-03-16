from functools import lru_cache
from typing import Iterable

from entities.cards import Suit, SUITS, Card, Value, VALUES, ZERO_ACE


class Combination:
    def __init__(self, priority: int, func, name):
        self.priority: int = priority
        self.func = func
        self.name = name

    def check(self, cards) -> tuple:
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
    """find how many dulpicates are present in the known cards"""
    _duplicates = {}
    for value in VALUES:
        _duplicates[value] = len([card for card in cards if card.value == value])
    return _duplicates


def _card_ranges() -> list[tuple[Value]]:
    """all possible ranges for straights"""
    _values = (ZERO_ACE,) + VALUES
    return [tuple(_values[value_index] for value_index in range(i, i+5)) for i in range(len(_values[:-4]))]


CARD_RANGES = _card_ranges()


def cards_in_ranges(cards: [list[Card], tuple[Card]]) -> dict[Value: int]:
    _cards = list(cards)
    _cards_in_ranges = {}
    # duplicate aces for a-to-5 straights
    card_values_set = set(c.value for c in _cards)
    if Value(14, 'Ace', 'A') in card_values_set:
        card_values_set.add(ZERO_ACE)
    # count uniq values of given cards for each straight range
    for _range in CARD_RANGES:
        _cards_in_ranges[_range] = len(set(_range).intersection(card_values_set))
    return _cards_in_ranges


def cards_by_suit(cards: [list[Card], tuple[Card]]) -> dict[Suit: int]:
    return {suit: len([card for card in cards if card.suit == suit]) for suit in SUITS}


def high_card(cards: Iterable[Card]) -> [None, tuple[Card, list[Card]]]:
    if not cards:
        return None
    _cards = sorted(cards, key=lambda c: c.value, reverse=True)
    return _cards[0], _cards[1:min(5, len(_cards))]


def pair(cards: Iterable[Card]) -> [None, tuple[Value, list[Card]]]:
    values = set(card.value for card in cards)
    pair_values = []
    for value in values:
        if len([card for card in cards if card.value == value]) == 2:
            pair_values.append(value)
    if len(pair_values) == 1:
        return pair_values[0], sorted([card for card in cards if card.value != pair_values[0]],
                                      key=lambda c: c.value,
                                      reverse=True)[:3]
    else:
        return None


def two_pairs(cards: list[Card]) -> [None, tuple[Value, Value, Card]]:
    if len(cards) < 4:
        return None
    values = set(card.value for card in cards)
    pair_values: list[Value] = []
    for value in values:
        if len([card for card in cards if card.value == value]) == 2:
            pair_values.append(value)
    pair_values.sort(reverse=True)
    if len(pair_values) >= 2:
        try:
            return pair_values[0], pair_values[1], max([card for card in cards if card.value not in pair_values[:2]],
                                                       key=lambda c: c.value)
        except ValueError:
            return pair_values[0], pair_values[1], None
    else:
        return None


def three_of_a_kind(cards: list[Card]) -> [None, tuple[Value, list[Card]]]:
    if len(cards) < 3:
        return None
    values = set(card.value for card in cards)
    set_values = []
    for value in values:
        if len([card for card in cards if card.value == value]) == 3:
            set_values.append(value)
    if len(set_values) == 1:
        return set_values[0], sorted([card for card in cards if card.value != set_values[0]],
                                     key=lambda c: c.value,
                                     reverse=True)[:2]
    else:
        return None


def _in_a_row(values: list[Value]) -> bool:
    for i, v in enumerate(values[:-1]):
        if v.order + 1 != values[i+1].order:
            return False
    return True


def straight(cards: list[Card]) -> [None, list[Value]]:
    if len(cards) < 5:
        return None
    _cards = list(cards)
    # duplicate aces for a-to-5 straights
    for ace in (card for card in cards if card.value == Value(14, 'Ace', 'A')):
        _cards.append(Card(ace.suit, ZERO_ACE))
    # sort cards by values
    card_values = set(c.value for c in _cards)
    if len(card_values) < 5:
        return None
    else:
        max_range = len(card_values) - 4
    sorted_cards_values = sorted(card_values)
    # try to find a sequence of sorted cards
    for i in list(range(0, max_range))[::-1]:
        current_range = sorted_cards_values[0+i: 5+i]
        if _in_a_row(current_range):
            return current_range[-1]
    return None


def flush(cards: list[Card]) -> [None, list[Card]]:
    if len(cards) < 5:
        return None
    for suit in SUITS:
        flush_cards = [card for card in cards if card.suit == suit]
        if len(flush_cards) >= 5:
            return sorted(flush_cards, key=lambda c: c.value, reverse=True)[:5]
    return None


def full_house(cards: list[Card]) -> [None, tuple[Value, Value]]:
    if len(cards) < 5:
        return None
    values = set(card.value for card in cards)
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
    elif len(set_values) == 2:
        set_values.sort(reverse=True)
        return set_values[0], set_values[1]
    else:
        return None


def four_of_a_kind(cards: list[Card]) -> [None, tuple[Value, Value]]:
    if len(cards) < 4:
        return None
    values = set(card.value for card in cards)
    four_values: list[Value] = []
    for value in values:
        if len([card for card in cards if card.value == value]) == 4:
            four_values.append(value)
    if len(four_values) == 1:
        try:
            return four_values[0], max(card.value for card in cards if card.value not in four_values)
        except ValueError:
            return four_values[0], None
    else:
        return None


def straight_flush(cards: list[Card]) -> [None, list[Card]]:
    _cards = list(cards)
    # duplicate aces for a-to-5 straights
    for ace in (card for card in cards if card.value == Value(14, 'Ace', 'A')):
        _cards.append(Card(ace.suit, ZERO_ACE))
    # sort cards by values
    card_values = set(c.value for c in _cards)
    if len(card_values) < 5:
        return None
    else:
        max_range = len(card_values) - 4
    sorted_cards_values = sorted(card_values)
    # try to find a sequence of sorted cards
    for i in list(range(0, max_range))[::-1]:
        current_range = sorted_cards_values[0 + i: 5 + i]
        range_cards = [card for card in _cards if card.value in current_range]
        if _in_a_row(current_range) and (f := flush(range_cards)):
            return f


def royal_flush(cards: list[Card]) -> [None, list[Card]]:
    _straight_flush = straight_flush(cards)
    if _straight_flush and _straight_flush[0].value == Value(14, 'Ace', 'A'):
        return _straight_flush
    else:
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
def best_hand(cards: tuple[Card]) -> tuple[Combination, tuple]:
    for combination in COMBINATIONS:
        found = combination.check(cards)
        if found:
            return combination, found


if __name__ == '__main__':
    from cards import Deck
    print(*_card_ranges(), sep='\n')
    print(cards_in_ranges(list(Deck.all_cards())))