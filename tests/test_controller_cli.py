import pytest

from controller import cli
from entities.bet import Bet, Decision
from entities.players import Player


@pytest.mark.parametrize(
    "input_str, expected_decision, expected_error",
    [
        ("fold", Decision(Bet.FOLD), ""),
        ("check", Decision(Bet.CHECK), ""),
        ("call", Decision(Bet.CALL), ""),
        ("all-in", Decision(Bet.ALL_IN), ""),
        ("raise 100", Decision(Bet.RAISE, 100.0), ""),
        ("bluff", None, "There's no such action"),
        ("raise abc", None, "Invalid bet amount. It must be a floating point number"),
        ("raise 1 2", None, "You must input an action and the amount in case of raise")
    ]
)
def test_text_to_bet(input_str, expected_decision, expected_error):
    decision, error = cli.text_to_bet(input_str)
    assert decision == expected_decision
    assert error == expected_error


class TestMakePlayersDecision:
    zero_bet_allowed_actions = [Bet.CHECK, Bet.FOLD, Bet.RAISE, Bet.ALL_IN]
    non_zero_bet_allowed_actions = [Bet.FOLD, Bet.CALL, Bet.RAISE, Bet.ALL_IN]

    @pytest.fixture
    def player(self):
        return Player(100)

    @pytest.mark.parametrize(
        'decision, requested_bet, allowed_actions, expected_decision, expected_money, expected_error',
        [
            # valid decisions
            (Decision(Bet.FOLD), 0, zero_bet_allowed_actions, Decision(Bet.FOLD), 100, ''),
            (Decision(Bet.CHECK), 0, zero_bet_allowed_actions, Decision(Bet.CHECK), 100, ''),
            (Decision(Bet.CALL), 50, [Bet.CALL], Decision(Bet.CALL, 50), 50, ''),
            (Decision(Bet.RAISE, 50), 0, zero_bet_allowed_actions, Decision(Bet.RAISE, 50), 50, ''),
            (Decision(Bet.RAISE, 120), 0, zero_bet_allowed_actions, Decision(Bet.ALL_IN, 100), 0, ''),
            (Decision(Bet.ALL_IN), 0, zero_bet_allowed_actions, Decision(Bet.ALL_IN, 100), 0, ''),
            # invalid decisions
            (Decision(Bet.CHECK), 50, non_zero_bet_allowed_actions,
             Decision(Bet.NOT_DECIDED), 100, "You can't choose this decision"),
            (Decision(Bet.RAISE, -50), 50, non_zero_bet_allowed_actions,
             Decision(Bet.NOT_DECIDED), 100, "You must enter positive bet"),
            (Decision(Bet.RAISE, 50), 99, non_zero_bet_allowed_actions,
             Decision(Bet.NOT_DECIDED), 100, "The bet must not be lower than the current bet")
        ]
    )
    def test_decision(self, player: Player,
                      decision: Decision,
                      requested_bet: float,
                      allowed_actions: list[Bet],
                      expected_decision: Decision,
                      expected_money: float,
                      expected_error: str):
        player.requested_bet = requested_bet
        player.available_actions = allowed_actions
        error = cli.make_players_decision(player, decision)
        assert player.decision == expected_decision
        assert error == expected_error
        assert player.stack == expected_money
