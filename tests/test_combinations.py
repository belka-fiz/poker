from random import sample, choice, shuffle, randint

import pytest

from entities import combinations
from entities.cards import VALUES, SUITS, Card


def test_cards_in_ranges():
    # todo
    pass


expected_pairs = [
    [
        Card(SUITS[0], VALUES[0]),
        Card(SUITS[2], VALUES[0]),
        Card(choice(SUITS), VALUES[2]),
        Card(choice(SUITS), VALUES[3]),
        Card(choice(SUITS), VALUES[4]),
        Card(choice(SUITS), VALUES[6]),
        Card(choice(SUITS), VALUES[8])
    ],
    [Card(suit, VALUES[3]) for suit in sample(SUITS, 2)] + [Card(choice(SUITS), value) for value in
                                                            sample(VALUES[4:], 5)]
]


@pytest.mark.parametrize('cards', expected_pairs, ids=str)
def test_pair(cards):
    shuffle(cards)
    assert combinations.pair(cards), f'{cards} do not form a pair'
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'pair'


def test_two_pairs():
    cards = []
    for value in sample(VALUES[5:], 2):
        cards += [Card(suit, value) for suit in sample(SUITS, 2)]
    cards += [Card(choice(SUITS), value) for value in sample(VALUES[:5], 3)]
    shuffle(cards)
    assert combinations.two_pairs(cards), f'{cards} do not form two pairs'
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'two_pairs'


def test_three():
    cards = [Card(suit, VALUES[1]) for suit in sample(SUITS, 3)]
    cards += [Card(choice(SUITS), value) for value in sample(VALUES[2:], 4)]
    shuffle(cards)
    assert combinations.three_of_a_kind(cards), f'{cards} do not form three of a kind'
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'three_of_a_kind'


@pytest.mark.parametrize('offset', range(14-5))
def test_straight(offset: int):
    cards = [Card(choice(SUITS), value) for value in VALUES[offset:offset+5]]
    cards += [Card(choice(SUITS), choice(VALUES)) for _ in range(2)]
    shuffle(cards)
    assert combinations.straight(cards), f'{cards} do not form a straight'
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'straight'


def test_straight_zero_ace():
    """test for straight from Ace to 5"""
    pass


@pytest.mark.parametrize('suit', SUITS, ids=str)
def test_flush(suit):
    _values = list(VALUES)
    cards = [Card(suit, _values.pop(randint(0, len(_values) - 1))) for _ in range(5)]
    shuffle(cards)
    print(cards)
    assert combinations.flush(cards), f'{cards} do not form a flush'
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'flush'


def test_full_house():
    values = sample(VALUES, 2)
    cards = [Card(suit, values[0]) for suit in sample(SUITS, 3)] + [Card(suit, values[1]) for suit in sample(SUITS, 3)]
    cards += [Card(choice(SUITS), choice(list(set(VALUES)-set(values)))) for _ in range(2)]
    shuffle(cards)
    assert combinations.full_house(cards), f'{cards} do not form a full house'
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'full_house'


def test_four_of_a_kind():
    value = choice(VALUES)
    cards = [Card(suit, value) for suit in SUITS]
    other_values = set(VALUES)
    other_values.discard(value)
    cards += [Card(choice(SUITS), choice(list(other_values))) for _ in range(3)]
    shuffle(cards)
    assert combinations.four_of_a_kind(cards), f'{cards} do not form a four of a kind'
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'four_of_a_kind'


def test_straight_flush():
    values = VALUES[3:10]
    cards = [Card(SUITS[0], values[i]) for i in range(5)] + [Card(SUITS[1], values[i]) for i in range(5, 7)]
    shuffle(cards)
    assert combinations.straight_flush(cards), f'{cards} do not form a straight flush'
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'straight_flush'


def test_royal_flush():
    values = VALUES[-5:]
    cards = [Card(SUITS[-1], value) for value in values] + [Card(choice(SUITS[:-1]), choice(VALUES)) for _ in range(2)]
    shuffle(cards)
    assert combinations.royal_flush(cards)
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'royal_flush'


def test_combinations_order():
    """test that combinations are sorted in the right order"""
    # todo
    pass


