import pytest

from entities.game import Round
from entities.players import Player


@pytest.fixture(scope='class')
def game_round() -> Round:
    players = [Player(300) for _ in range(2)]
    game_round = Round(players, 0, 10, debug=True)
    return game_round


@pytest.mark.usefixtures('game_round')
class TestRoundCards:
    """Make sure cards are given in the right amount on the right stages"""

    def test_deck_is_reset_at_the_start_of_the_round(self, game_round):
        assert game_round.deck.cards_left == 52

    def test_players_are_given_two_cards_at_pre_flop(self, game_round):
        game_round.deal_players_cards()
        game_round.stage_index += 1
        game_round.new_stage()
        assert game_round.stage_name == 'pre-flop'
        for player in game_round.players:
            assert len(player.hand) == 2

    def test_three_community_cards_are_open_on_flop(self, game_round):
        game_round.stage_index += 1
        game_round.new_stage()
        assert game_round.stage_name == 'flop'
        assert len(game_round.board) == 3

    def test_one_community_card_is_open_on_turn(self, game_round):
        game_round.stage_index += 1
        game_round.new_stage()
        assert game_round.stage_name == 'turn'
        assert len(game_round.board) == 4

    def test_one_community_card_is_open_on_river(self, game_round):
        game_round.stage_index += 1
        game_round.new_stage()
        assert game_round.stage_name == 'river'
        assert len(game_round.board) == 5


@pytest.mark.skip(reason="Not implemented")
class TestBetsCollection:
    """Make sure the bets are subtracted from the players stacks and added to the pot"""

    def test_folder_is_excluded(self):
        pass

    def test_callers_contribute_the_same_amount(self):
        pass

    def test_all_in_and_call_contribute_the_same(self):
        pass

    def test_raise_over_all_in_makes_different_contribution(self):
        pass

    def test_all_in_instead_of_blind(self):
        pass


class TestWinners:
    """Make sure winners are defined right and the prize is distributed to the right people in the right amount"""
