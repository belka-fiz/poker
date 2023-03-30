from entities.cards import Deck, Value


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


def test_values_order():
    pass


def test_suits_do_not_make_difference_in_cards_value():
    pass


def test_card_names():
    """make sure the name is formed from the Value and Suit right"""
    pass
