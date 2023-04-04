from secrets import SystemRandom
from typing import Union

from ai.ai import AI
from config import DEFAULT_PLAYERS_NUM, DEFAULT_BUY_IN, DEFAULT_BLIND
from controller.cli import ask_for_int_input, ask_for_str_input, ask_for_bool_input
from data.constants import NAMES
from entities.game import Game, Player
from errors import errors

random = SystemRandom()


def start_a_game(number_of_players: int, init_chips: float, blind: float, player_name: str) -> None:
    """
    Create a new game with pre-defined number of AI players
    :param number_of_players: number of total players, including human
    :param init_chips: The size of each player's stack at the start
    :param blind: The initial blinds size
    :param player_name: Name of a human player
    :return: None
    """
    # create AI players and assign uniq names to them
    names = NAMES.copy()
    players: list[Union[Player, AI]]
    players = [AI(init_chips, name=names.pop(random.randint(0, len(names)))) for _ in range(number_of_players - 1)]
    # add one human player
    players.append(Player(init_chips, is_ai=False, name=player_name))
    # create the game and add the players
    game = Game(blind, init_chips, continuous=False)
    for player in players:
        game.add_player(player)
    # start a new game round while there are at least 2 players, including AI
    while True:
        try:
            game.new_round()
        except errors.NotEnoughPlayers:
            break
    # list the players and their stacks at the end of the game
    for player in players:
        print(f"{player.name}'s stack is {player.stack}")


def main():
    """
    Start a CLI game for 1 human and a configurable number of AI players
    :return: None
    """
    player_name = ask_for_str_input()
    quick_game = ask_for_bool_input('Would you like to start a quick game?')
    # create a single-player game with default params
    if quick_game:
        number_of_players = DEFAULT_PLAYERS_NUM
        init_chips = DEFAULT_BUY_IN
        blind_size = DEFAULT_BLIND
    # create a custom single-player game
    else:
        number_of_players = ask_for_int_input('number of players', (2, 7), (3, 5))
        init_chips = ask_for_int_input('initial chips', (100, 100_000), (300, 10_000))
        blind_size = ask_for_int_input('blind size', (init_chips // 100, init_chips // 5),
                                       (init_chips // 50, init_chips // 10))
    start_a_game(number_of_players, init_chips, blind_size, player_name)


if __name__ == '__main__':
    main()
