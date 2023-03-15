from pprint import pprint
from secrets import SystemRandom

from controller.cli import ask_for_input, ask_for_name
from data.constants import NAMES
from entities.combinations import best_hand
from entities.game import Game, Player
from errors import errors

random = SystemRandom()


def start_a_game(number_of_players, init_chips, blind, player_name):
    players = [Player(init_chips, name=random.choice(NAMES)) for _ in range(number_of_players - 1)]
    players.append(Player(init_chips, is_ai=False))
    game = Game(blind, init_chips, continuous=False)
    for player in players:
        game.add_player(player)
    while True:
        try:
            new_round = game.new_round()
            if len(new_round._active_players) > 1:
                for player in players:
                    if player in new_round.players:
                        print(player.hand)
                        print(best_hand(new_round.board + player.hand) if player.is_active else None)
                        if player in new_round.winners:
                            print('Player is winner')
            pprint(new_round.get_status(), indent=2)
            print()
        except errors.NotEnoughPlayers:
            break
    for player in players:
        print(player.stack)


def main():
    player_name = ask_for_name()
    number_of_players = ask_for_input('number of players', (2, 7), (3, 5))
    init_chips = ask_for_input('initial chips', (100, 100_000), (300, 10_000))
    blind_size = ask_for_input('blind size', (init_chips // 100, init_chips // 5), (init_chips // 50, init_chips // 10))
    start_a_game(number_of_players, init_chips, blind_size, player_name)


if __name__ == '__main__':
    main()
