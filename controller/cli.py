from common.event import EventType, subscribe
from entities.bet import Bet, Decision
from entities.cards import Card
from entities.players import Player
from entities.round import Round
from errors.errors import UnavailableDecision, NegativeBetError, TooSmallBetError


def text_to_bet(input_str: str) -> tuple[[Decision, None], str]:
    """Creates a Decision object from the provided user input string and handling errors"""
    input_values = input_str.split(' ')
    if len(input_values) not in [1, 2]:
        return None, "You must input an action and the amount in case of raise"

    if len(input_values) == 2:
        action, bet_size = input_values
    else:
        action = input_values[0]
        bet_size = 0

    try:
        return Decision(Bet[action.replace('-', '_').upper()], float(bet_size)), ''
    except KeyError:
        return None, "There's no such action"
    except ValueError:
        return None, "Invalid bet amount. It must be a floating point number"


def make_players_decision(player: Player, decision: Decision) -> str:
    """Acts the player's Decision and handling errors"""
    error_msg = ''
    try:
        player.decide(decision)
    except UnavailableDecision:
        error_msg = "You can't choose this decision"
    except NegativeBetError:
        error_msg = "You must enter positive bet"
    except TooSmallBetError:
        error_msg = "The bet must not be lower than the current bet"
    return error_msg


def game_cli_action(player: Player, board: [tuple[Card], list[Card]], bet_size):
    """Player interaction during the game"""
    prompt = f"Choose your bet. Your cards: {player.hand}, the board: {board}\n" \
             f"Your stack is {player.stack}. Your current bet is {player.decision.size}\n" \
             f"Your variants: {player.available_actions}. The bet is {bet_size}"
    while True:
        input_str = input(prompt + '\n')
        decision, prompt = text_to_bet(input_str)
        if prompt:
            continue
        prompt = make_players_decision(player, decision)
        if not prompt:
            break


def game_cli_action_by_round(player: Player, game_round: Round):
    """Temp adapter for calling game_cli_action from events"""
    if not player.is_ai:
        game_cli_action(player, game_round.board, player.requested_bet)


def ask_for_int_input(parameter: str, domain: tuple[int, int], suggested_range: tuple[int, int]) -> int:
    """
    Ask for int value for game configuration having suggested and valid ranges
    It is checked that the value can be converted to int, and that it is within the domain.
    """
    prompt = f"Please, input the {parameter} from {domain[0]} to {domain[1]}.\r\n" \
             f"We suggest the range between {suggested_range[0]} and {suggested_range[1]}.\r\n"
    while True:
        value = input(prompt)
        try:
            int_value = int(value)
        except ValueError:
            continue
        if domain[0] <= int_value <= domain[1]:
            return int_value


def ask_for_str_input(prompt="Hi! What's your name?\r\n") -> str:
    """
    Ask for a string input.
    Used mainly for the name input, so the default prompt is about the name
    No validations except that the string is not empty
    """
    while not (name := input(prompt)):
        continue
    return name


def ask_for_bool_input(prompt) -> bool:
    """
    Asks for a bool value.
    Ensures that user enters 'y' or 'n'. The case doesn't matter.
    """
    print(prompt)
    bool_prompt = "Please, enter 'y' or 'n'!\n"
    while (val := input(bool_prompt).lower()) not in ['y', 'n']:
        continue
    return val == 'y'


subscribe(EventType.PLAYER_MAKE_MOVE, game_cli_action_by_round)
