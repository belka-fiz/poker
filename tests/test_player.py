import pytest

from entities.bet import Bet, Decision
from entities.cards import Card, SUITS, VALUES
from entities.players import Player
from errors.errors import TooSmallBetError, TooManyCards


@pytest.fixture(scope='function')
def test_player():
    player = Player(500, is_ai=False)
    player.add_card(Card(SUITS[0], VALUES[1]))
    player.add_card(Card(SUITS[0], VALUES[2]))
    return player


@pytest.mark.skip
class TestInit:
    def test_init_ai(self):
        raise NotImplementedError

    def test_init_human(self):
        raise NotImplementedError


class TestBets:
    @staticmethod
    def _verify_decision(player: Player,
                         decision: Decision,
                         made_decision=True,
                         in_the_game=True):
        assert player.made_decision is made_decision
        assert player.decision == decision
        assert player.is_active is in_the_game

    def test_blind(self, test_player):
        test_player.post_blind(50)
        self._verify_decision(test_player, Decision(Bet.BLIND, 50), False)

    def test_blind_over_stack(self, test_player):
        test_player.post_blind(501)
        self._verify_decision(test_player, Decision(Bet.ALL_IN, 500))

    def test_check_over_zero(self, test_player):
        test_player.ask_for_a_decision(0)
        test_player.decide(Decision(Bet.CHECK))
        self._verify_decision(test_player, Decision(Bet.CHECK, 0))

    def test_check_over_blind(self, test_player):
        test_player.post_blind(10)
        test_player.ask_for_a_decision(10)
        test_player.decide(Decision(Bet.CHECK))
        self._verify_decision(test_player, Decision(Bet.CHECK, 10))

    def test_call(self, test_player):
        test_player.ask_for_a_decision(10)
        test_player.decide(Decision(Bet.CALL))
        self._verify_decision(test_player, Decision(Bet.CALL, 10))

    def test_raise_simple(self, test_player):
        test_player.ask_for_a_decision(20)
        test_player.decide(Decision(Bet.RAISE, 40))
        self._verify_decision(test_player, Decision(Bet.RAISE, 40))

    def test_raise_simple_zero(self, test_player):
        test_player.ask_for_a_decision(0)
        test_player.decide(Decision(Bet.RAISE, 0))
        self._verify_decision(test_player, Decision(Bet.CHECK, 0))

    def test_raise_under_requested(self, test_player):
        test_player.ask_for_a_decision(20)
        with pytest.raises(TooSmallBetError):
            test_player.decide(Decision(Bet.RAISE, 10))
        self._verify_decision(test_player, Decision(Bet.NOT_DECIDED), made_decision=False)

    def test_raise_equal_to_requested(self, test_player):
        test_player.ask_for_a_decision(20)
        test_player.decide(Decision(Bet.RAISE, 20))
        self._verify_decision(test_player, Decision(Bet.CALL, 20))

    def test_raise_over_stack(self, test_player):
        test_player.ask_for_a_decision(20)
        test_player.decide(Decision(Bet.RAISE, 501))
        self._verify_decision(test_player, Decision(Bet.ALL_IN, 500))

    def test_all_in(self, test_player):
        test_player.ask_for_a_decision(20)
        test_player.decide(Decision(Bet.ALL_IN))
        self._verify_decision(test_player, Decision(Bet.ALL_IN, 500))

    def test_fold_having_no_bet(self, test_player):
        test_player.ask_for_a_decision(20)
        test_player.decide(Decision(Bet.FOLD))
        self._verify_decision(test_player, Decision(Bet.FOLD), in_the_game=False)

    def test_fold_after_blind(self, test_player):
        test_player.post_blind(10)
        test_player.ask_for_a_decision(20)
        test_player.decide(Decision(Bet.FOLD))
        self._verify_decision(test_player, Decision(Bet.FOLD, 10), in_the_game=False)

    def test_fold_after_bet(self, test_player):
        test_player.ask_for_a_decision(20)
        test_player.decide(Decision(Bet.CALL))
        test_player.ask_for_a_decision(40)
        test_player.decide(Decision(Bet.FOLD))
        self._verify_decision(test_player, Decision(Bet.FOLD, 20), in_the_game=False)


class TestReset:
    @staticmethod
    def _verify_reset(
            player: Player,
            expected_decision: Decision = Decision(Bet.NOT_DECIDED),
            expected_hand_reset=False,
            expected_all_in=False,
            expected_in_the_game=True
    ):
        assert player.decision == expected_decision, "Decision is not reset properly"
        assert (len(player.hand) == 0) is expected_hand_reset, "The hand is not reset"
        assert player.is_all_in is expected_all_in, "The all in is not reset properly"
        assert player.made_decision is expected_all_in, "Made decision flag is not reset properly"
        assert player.is_active is expected_in_the_game, "Active flag is not reset properly"
        assert not player.available_actions, "Available actions are not reset properly"
        assert not player.requested_bet, "Requested bet is not reset properly"

    def test_new_stage(self, test_player):
        test_player.ask_for_a_decision(10)
        test_player.decide(Decision(Bet.CALL))
        test_player.new_stage()
        self._verify_reset(test_player)

    def test_new_stage_fold(self, test_player):
        test_player.ask_for_a_decision(10)
        test_player.decide(Decision(Bet.FOLD))
        test_player.new_stage()
        self._verify_reset(test_player, expected_in_the_game=False, expected_hand_reset=True)

    def test_new_stage_all_in(self, test_player):
        test_player.ask_for_a_decision(10)
        test_player.decide(Decision(Bet.ALL_IN))
        test_player.new_stage()
        self._verify_reset(test_player, expected_decision=Decision(Bet.ALL_IN, 0), expected_all_in=True)

    def test_new_game_round(self, test_player):
        test_player.ask_for_a_decision(10)
        test_player.decide(Decision(Bet.CALL))
        test_player.new_game_round()
        self._verify_reset(test_player, expected_hand_reset=True)

    def test_reset_decision(self, test_player):
        test_player.ask_for_a_decision(10)
        test_player.decide(Decision(Bet.CALL))
        assert test_player.made_decision, "Made decision flag is not set after bet"
        test_player.reset_decision()
        assert not test_player.made_decision, "Made decision flag is not reset"


class TestCards:
    def test_add_one(self, test_player):
        test_player.new_game_round()
        test_player.add_card(Card(SUITS[-1], VALUES[-1]))
        assert len(test_player.hand) == 1

    def test_add_two(self, test_player):
        test_player.new_game_round()
        test_player.add_card(Card(SUITS[-1], VALUES[-1]))
        test_player.add_card(Card(SUITS[-1], VALUES[-2]))
        assert len(test_player.hand) == 2

    def test_overflow(self, test_player):
        test_player.new_game_round()
        test_player.add_card(Card(SUITS[-1], VALUES[-1]))
        test_player.add_card(Card(SUITS[-1], VALUES[-2]))
        with pytest.raises(TooManyCards):
            test_player.add_card(Card(SUITS[-1], VALUES[-3]))
