import pytest

from entities.cards import Deck, Value, Card, VALUES, SUITS


def test_all_cards_hashes_are_uniq():
    """compare all hashes and make sure there are 52 different"""
    hashes = {hash(card) for card in Deck.all_cards()}
    assert len(hashes) == 52, "Hashes are not unique"


def test_drawing_a_card_reduces_the_deck():
    deck = Deck()
    for i in range(52):
        deck.draw_one()
        assert deck.cards_left == 51 - i
    assert len(deck.all_cards()) == 52


def test_hiding_a_card_reduces_the_deck():
    deck = Deck()
    for i in range(52):
        deck.hide_one()
        assert deck.cards_left == 51 - i


def test_shuffle_makes_different_order():
    deck = Deck()
    initial_order = deck._order.copy()
    matches = 0
    deck.mix()
    assert len(deck._order) == len(initial_order) == 52
    for i in range(52):
        if deck._order[i] == initial_order[i]:
            matches += 1
    assert matches < 30


def test_card_values_equality():
    a = Value(14, 'Ace', 'A')
    b = Value(14, 'Ace', 'A')
    assert a == b


@pytest.mark.parametrize(('value1', 'value2'), [(VALUES[i], VALUES[i+1]) for i in range(len(VALUES)-1)], ids=str)
def test_values_are_ordered(value1, value2):
    assert value1 < value2, ""


@pytest.mark.parametrize('value', [v for v in VALUES], ids=str)
def test_suits_do_not_make_difference_in_cards_value(value):
    card_1 = Card(SUITS[0], value)
    card_2 = Card(SUITS[1], value)
    card_3 = Card(SUITS[2], value)
    card_4 = Card(SUITS[3], value)
    assert card_1 == card_2 == card_3 == card_4, "Cards with the same value and different suits are not equal"


def test_card_names():
    """The name of card should be formed from the Value and Suit right"""
    a = Card(SUITS[0], Value(14, 'Ace', 'A'))
    assert str(a) == str(a.value) + str(a.suit)


def test_card_repr():
    """The name of card should be formed from the Value and Suit right"""
    a = Card(SUITS[0], Value(14, 'Ace', 'A'))
    assert repr(a) == repr(a.value) + repr(a.suit)
