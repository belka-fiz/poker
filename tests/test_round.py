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
    def test_deck_is_reset_at_the_start_of_the_round(self, game_round):
        assert game_round.deck.cards_left == 52

    def test_players_are_given_two_cards_at_pre_flop(self, game_round):
        game_round.deal_players_cards()
        game_round.new_stage()
        assert game_round.get_status()['stage'] == 'pre-flop'
        for player in game_round.players:
            assert len(player.hand) == 2

    def test_three_community_cards_are_open_on_flop(self, game_round):
        game_round.new_stage()
        assert game_round.get_status()['stage'] == 'flop'
        assert len(game_round.board) == 3

    def test_one_community_card_is_open_on_turn(self, game_round):
        game_round.new_stage()
        assert game_round.get_status()['stage'] == 'turn'
        assert len(game_round.board) == 4

    def test_one_community_card_is_open_on_river(self, game_round):
        game_round.new_stage()
        assert game_round.get_status()['stage'] == 'river'
        assert len(game_round.board) == 5
