from pprint import pprint
from secrets import SystemRandom

from config import DEFAULT_PLAYERS_NUM, DEFAULT_BUY_IN, DEFAULT_BLIND
from controller.cli import ask_for_int_input, ask_for_str_input, ask_for_bool_input
from data.constants import NAMES
from entities.combinations import best_hand
from entities.game import Game, Player
from errors import errors

random = SystemRandom()


def start_a_game(number_of_players, init_chips, blind, player_name):
    # create AI players and assign uniq names to them
    names = NAMES.copy()
    players = [Player(init_chips, name=names.pop(random.randint(0, len(names)))) for _ in range(number_of_players - 1)]
    # add one human player
    players.append(Player(init_chips, is_ai=False, name=player_name))
    # create the game and add the players
    game = Game(blind, init_chips, continuous=False)
    for player in players:
        game.add_player(player)
    # start a new game round while there are at least 2 players, including AI
    while True:
        try:
            new_round = game.new_round()
            # print winners and their hands if there are more than ont player left at the end of the round
            if len(new_round.active_players) > 1:
                for player in players:
                    if player in new_round.players:
                        print(player.hand)
                        print(best_hand(new_round.board + player.hand) if player.is_active else None)
                        if player in new_round.winners:
                            print('Player is winner')
            # print the status of the round at its end
            pprint(new_round.get_status(), indent=2)
            print()
        except errors.NotEnoughPlayers:
            break
    # list the players and their stacks at the end of the game
    for player in players:
        print(f"{player.name}'s stack is {player.stack}")


def main():
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