from random import sample, choice, shuffle, randint

import pytest

from entities import combinations
from entities.cards import VALUES, SUITS, Card, Deck


@pytest.mark.parametrize(('rng', 'cards'), combinations.cards_in_ranges(list(Deck.all_cards())).items(), ids=str)
def test_cards_in_ranges(rng, cards):
    assert cards == 5, f"Not 5 cards are found in a full deck in range {rng}"


@pytest.mark.parametrize(('cards', 'number'), [
    (tuple(Card(suit, VALUES[3]) for suit in sample(SUITS, 2)) + tuple(Card(choice(SUITS), value) for value in
                                                                       sample(VALUES[4:], 5)), 2),
    (tuple(Card(suit, VALUES[1]) for suit in sample(SUITS, 3)), 3),
    (tuple(Card(suit, VALUES[10]) for suit in sample(SUITS, 4)), 4)
], ids=str)
def test_duplicates(cards, number):
    duplicates = combinations.duplicates(cards)
    assert max(duplicates.values()) == number


@pytest.mark.parametrize(('suit', 'number'), combinations.cards_by_suit(list(Deck.all_cards())).items(), ids=str)
def test_suited(suit, number):
    assert number == 13, f"There were not 13 cards found for {suit} suit in the whole deck"


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


def test_high_card_empty():
    assert combinations.high_card([]) is None, "No cards High Card is not None"


def test_high_card_not_empty():
    high_card = Card(SUITS[3], VALUES[-2])
    cards = [Card(SUITS[0], v) for v in VALUES[1:5]] + [high_card]
    assert combinations.high_card(cards)[0] == high_card
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'high_card'


def test_high_card_order_combinations():
    high_card_1 = Card(SUITS[3], VALUES[-2])
    cards_1 = [Card(SUITS[0], v) for v in VALUES[1:5]] + [high_card_1]
    high_card_2 = Card(SUITS[2], VALUES[-3])
    cards_2 = [Card(SUITS[1], v) for v in VALUES[1:5]] + [high_card_2]
    assert combinations.best_hand(cards_2) < combinations.best_hand(cards_1)


def test_high_card_equal_combinations():
    high_card_1 = Card(SUITS[3], VALUES[-2])
    cards_1 = [Card(SUITS[0], v) for v in VALUES[1:5]] + [high_card_1]
    high_card_2 = Card(SUITS[2], VALUES[-2])
    cards_2 = [Card(SUITS[1], v) for v in VALUES[1:5]] + [high_card_2]
    assert combinations.best_hand(cards_1) == combinations.best_hand(cards_2)


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


def test_none_two_pairs_by_length():
    cards = []
    for value in sample(VALUES[5:], 2):
        cards += [Card(suit, value) for suit in sample(SUITS, 2)]
    cards.pop()
    assert combinations.two_pairs(cards) is None


def test_two_pairs_with_value_error():
    cards = []
    for value in sample(VALUES[5:], 2):
        cards += [Card(suit, value) for suit in sample(SUITS, 2)]
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


def test_none_three_by_length():
    cards = [Card(suit, VALUES[1]) for suit in sample(SUITS, 2)]
    assert combinations.three_of_a_kind(cards) is None


@pytest.mark.parametrize('offset', range(14 - 5))
def test_straight(offset: int):
    _suits = list(SUITS + SUITS)
    cards = [Card(_suits.pop(), value) for value in VALUES[offset:offset + 5]]
    cards += [Card(_suits.pop(), choice(VALUES)) for _ in range(2)]
    shuffle(cards)
    assert combinations.straight(cards), f'{cards} do not form a straight'
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'straight'


def test_none_straight_by_cards():
    _suits = list(SUITS)
    cards = [Card(_suits.pop(), v) for v in VALUES[:4]]
    assert combinations.straight(cards) is None


def test_none_straight_by_values():
    _suits = list(SUITS)
    cards = [Card(_suits.pop(), v) for v in VALUES[:4]] + [Card(SUITS[0], VALUES[2])]
    assert combinations.straight(cards) is None


def test_straight_zero_ace():
    """test for straight from Ace to 5"""
    ace = Card(SUITS[0], VALUES[-1])
    two_to_four = [Card(SUITS[1], v) for v in VALUES[:4]]
    cards = two_to_four + [ace]
    assert combinations.straight(cards), f"{cards} do not form an A-to-4 straight"
    combination = combinations.best_hand(cards)
    assert isinstance(combination, tuple)
    assert combination[0].name == 'straight'


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
    cards += [Card(choice(SUITS), choice(list(set(VALUES) - set(values)))) for _ in range(2)]
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


@pytest.mark.parametrize(('c1', 'c2'), [(combinations.COMBINATIONS[i], combinations.COMBINATIONS[i + 1])
                                        for i in range(len(combinations.COMBINATIONS) - 1)], ids=str)
def test_combinations_order(c1, c2):
    """test that combinations are sorted in the right order"""
    assert c1 > c2
