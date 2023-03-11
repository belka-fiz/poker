from random import sample, choice, shuffle, randint

import pytest

import combinations
from cards import VALUES, SUITS, Card, Deck

expected_pairs = [[
    Card(SUITS[0], VALUES[0]),
    Card(SUITS[2], VALUES[0]),
    Card(choice(SUITS), VALUES[2]),
    Card(choice(SUITS), VALUES[3]),
    Card(choice(SUITS), VALUES[4]),
    Card(choice(SUITS), VALUES[6]),
    Card(choice(SUITS), VALUES[8])
], [Card(suit, VALUES[5]) for suit in sample(SUITS, 2)] + [Card(choice(SUITS), value) for value in
                                                           sample(VALUES[6:], 5)]
]


def test_all_cards_hashes_are_uniq():
    hashes = set(hash(card) for card in Deck.all_cards())
    assert len(hashes) == 52, "Hashes are not unique"


@pytest.mark.parametrize('cards', expected_pairs, ids=str)
def test_pair(cards):
    shuffle(cards)
    assert combinations.pair(cards), f'{cards} do not form a pair'


def test_three():
    cards = [Card(suit, VALUES[1]) for suit in sample(SUITS, 3)]
    cards += [Card(choice(SUITS), value) for value in sample(VALUES[2:], 4)]
    shuffle(cards)
    assert combinations.three_of_a_kind(cards), f'{cards} do not form three of a kind'


def test_two_pairs():
    cards = []
    for value in sample(VALUES[5:], 2):
        cards += [Card(suit, value) for suit in sample(SUITS, 2)]
    cards += [Card(choice(SUITS), value) for value in sample(VALUES[:5], 3)]
    shuffle(cards)
    assert combinations.two_pairs(cards), f'{cards} do not form two pairs'


@pytest.mark.parametrize('offset', range(14-5))
def test_straight(offset: int):
    cards = [Card(choice(SUITS), value) for value in VALUES[offset:offset+5]]
    cards += [Card(choice(SUITS), choice(VALUES)) for _ in range(2)]
    shuffle(cards)
    assert combinations.straight(cards), f'{cards} do not form a straight'


@pytest.mark.parametrize('suit', SUITS, ids=str)
def test_flush(suit):
    _values = list(VALUES)
    cards = [Card(suit, _values.pop(randint(0, len(_values) - 1))) for _ in range(5)]
    shuffle(cards)
    print(cards)
    assert combinations.flush(cards), f'{cards} do not form a flush'


def test_full_house():
    values = sample(VALUES, 2)
    cards = [Card(suit, values[0]) for suit in sample(SUITS, 3)] + [Card(suit, values[1]) for suit in sample(SUITS, 3)]
    cards += [Card(choice(SUITS), choice(list(set(VALUES)-set(values)))) for _ in range(2)]
    shuffle(cards)
    assert combinations.full_house(cards), f'{cards} do not form a full house'


def test_four_of_a_kind():
    value = choice(VALUES)
    cards = [Card(suit, value) for suit in SUITS]
    other_values = set(VALUES)
    other_values.discard(value)
    cards += [Card(choice(SUITS), choice(list(other_values))) for _ in range(3)]
    shuffle(cards)
    assert combinations.four_of_a_kind(cards), f'{cards} do not form a four of a kind'


def test_straight_flush():
    values = VALUES[3:10]
    cards = [Card(SUITS[0], values[i]) for i in range(5)] + [Card(SUITS[1], values[i]) for i in range(5, 7)]
    shuffle(cards)
    assert combinations.straight_flush(cards), f'{cards} do not form a straight flush'


def test_royal_flush():
    values = VALUES[-5:]
    cards = [Card(SUITS[-1], value) for value in values] + [Card(choice(SUITS[:-1]), choice(VALUES)) for _ in range(2)]
    shuffle(cards)
    assert combinations.royal_flush(cards)
