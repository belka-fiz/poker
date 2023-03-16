from entities.cards import Card
from errors.errors import UnavailableDecision, NegativeBetError, TooSmallBetError
from entities.players import Player


def game_cli_action(player: Player, board: [tuple[Card], list[Card]], bet):
    """Player interaction during the game"""
    print(f"Choose your bet. Your cards: {player.hand}, the board: {board}")
    print(f"Your stack is {player.stack}. Your current bet is {player.get_bet}")
    print(f"Your variants: {player.ask_for_a_decision(bet)}. The bet is {bet}")
    while True:
        if len(input_values := input().split(' ')) not in [1, 2]:
            continue
        elif len(input_values) == 2:
            decision, bet = input_values
            try:
                player.decide(decision, float(bet))
                break
            except UnavailableDecision:
                print("You can't choose this decision")
            except NegativeBetError:
                print("You must enter positive bet")
            except TooSmallBetError:
                print("The bet must not be lower than the current bet")
        else:
            try:
                player.decide(input_values[0])
                break
            except UnavailableDecision:
                print("You can't choose this decision")


def ask_for_int_input(parameter: str, domain: tuple[int, int], suggested_range: tuple[int, int]) -> int:
    """Game configuration"""
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
        else:
            continue


def ask_for_name(prompt='') -> str:
    prompt = prompt or "Hi! What's your name?\r\n"
    while not (name := input(prompt)):
        continue
    return name


def ask_for_bool_input(prompt) -> bool:
    print(prompt)
    bool_prompt = "Please, enter 'y' or 'n'!\n"
    # prompt = " ".join([prompt, bool_prompt])
    while (val := input(bool_prompt).lower()) not in ['y', 'n']:
        # prompt = bool_prompt
        continue
    return val == 'y'
