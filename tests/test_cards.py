from entities.cards import Deck


def test_all_cards_hashes_are_uniq():
    """compare all hashes and"""
    hashes = set(hash(card) for card in Deck.all_cards())
    assert len(hashes) == 52, "Hashes are not unique"


def test_drawing_a_card_reduces_the_deck():
    deck = Deck()
    for i in range(52):
        deck.draw_one()
        assert deck.cards_left == 51 - i


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
