import pytest

from entities.players import Player
from entities.pot import Pot


@pytest.fixture(scope="module")
def players():
    return [Player(100, name=name) for name in ['Alice', 'Bob', 'Charlie']]


@pytest.fixture(scope="function")
def pot(players):
    return Pot(players)


def test_init(players, pot):
    assert players is not pot.players
    for player in players:
        assert pot._contributions[player] == 0.0
    assert pot.pot_size == 0.0
    assert not pot.pots


def test_add_chips(players, pot):
    pot.add_chips(players[0], 20)
    assert pot._contributions[players[0]] == 20
    assert pot.pot_size == 20
    pot.add_chips(players[1], 30)
    assert pot._contributions[players[1]] == 30
    assert pot.pot_size == 50
    pot.add_chips(players[0], 30)
    assert pot._contributions[players[0]] == 50
    assert pot.pot_size == 80


def test_add_zero_chips(players, pot):
    p1 = players[0]
    pot.add_chips(p1, 0)
    assert pot.pot_size == 0
    assert pot._contributions[p1] == 0


def test_remove_player(players):
    from entities.bet import Bet, Decision
    p3 = Player(100, name='Folder')
    test_pot = Pot(players + [p3])
    p3.ask_for_a_decision(100)
    p3.decide(Decision(Bet.FOLD))
    assert p3 not in test_pot.players
    assert p3 not in test_pot.get_active_players()
    assert p3 in test_pot._contributions.keys()


def test_get_active_players(players, pot):
    active_players = pot.get_active_players()
    assert len(active_players) == 3
    for player in players:
        assert player in active_players


def test_recalculate_pots_three_different(players, pot):
    # todo separate test into two
    p1, p2, p3 = players
    pot.add_chips(p1, 20)
    pot.add_chips(p2, 30)
    pot.add_chips(p3, 10)
    pot.recalculate_pots()
    assert len(pot.pots) == 3
    assert pot.pots[0] == ([p1, p2, p3], 30)
    assert pot.pots[1] == ([p1, p2], 20)
    assert pot.pots[2] == ([p2], 10)
    assert sum(ps for _, ps in pot.pots) == pot.pot_size
    pot.remove_player(p1)
    pot.recalculate_pots()
    assert len(pot.pots) == 2
    assert pot.pots[0] == ([p2, p3], 30)
    assert pot.pots[1] == ([p2], 30)
    assert sum(pot.size for pot in pot.pots) == pot.pot_size


def test_recalculate_pots_same_size(players, pot):
    for player in players:
        pot.add_chips(player, 50)
    pot.recalculate_pots()
    assert len(pot.pots) == 1
    assert pot.pots[0].size == len(players) * 50


def test_distribute_pot():
    """
    test pot distribution:
    one size - one winner
    several sizes - one winner from the biggest pot
    one player left - the winner
    three sizes, each time a different winner
    """
    pass
