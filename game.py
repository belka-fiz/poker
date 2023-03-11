# import time
from operator import itemgetter
from typing import Iterable

from ai.ai import PreFlopDecider, StageBetAI
from cards import Deck, Card
from errors.errors import NegativeBetError, NotEnoughPlayers, UnavailableDecision, TooSmallBetError
from players import Player, Account
from combinations import best_hand, Combination


def console_input(player: Player, board: [tuple[Card], list[Card]], bet):
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


class Game:
    def __init__(self, blind: float, buy_in: float, continuous: bool = False):
        self.initial_blind = blind
        self.buy_in = buy_in
        self.continuous = continuous
        self.blind: float = 0.0
        self.increase_blinds = 5  # todo make customizable
        self.players: list[Player] = []
        self.last_dealer_index: int = -1
        self.rounds_started = 0

    def add_human_player(self, account: Account):
        account.join_game(self, self.buy_in)

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players.pop(self.players.index(player))

    def raise_blind(self):
        self.blind = self.initial_blind * 2 ** (self.rounds_started // self.increase_blinds)

    def new_round(self):
        for player in self.players:
            if player.stack <= 0:
                if not self.continuous or not player.is_ai:
                    self.remove_player(player)
                elif player.is_ai:
                    player.add_money(self.buy_in)
        if len(self.players) < 2:
            raise NotEnoughPlayers
        self.raise_blind()
        new_round = Round(self.players, self.last_dealer_index, self.blind)
        self.last_dealer_index += 1
        if self.last_dealer_index >= len(self.players):
            self.last_dealer_index = 0
        self.rounds_started += 1
        return new_round

    def end_game(self):
        pass


class Round:
    STAGES = ('deal', 'pre-flop', 'flop', 'turn', 'river', 'showdown')
    NUMBER_OF_CARDS = {1: 0, 2: 3, 3: 1, 4: 1}

    def __init__(self, players: list[Player], dealer_index: int, blind_size: float):
        """Initialize the game"""
        self.blind_size = blind_size
        self._board: list[Card] = []
        self.pot: float = 0.0
        self.winners: list[Player] = []
        self.deck = Deck()
        self.players = players[dealer_index + 1:] + players[:dealer_index + 1]
        self._stage_index = 0
        self._deal_players_cards()

    @property
    def board(self):
        return tuple(self._board)

    def _deal_board(self, number):
        self.deck.hide_one()
        self._board.extend([self.deck.draw_one() for _ in range(number)])

    def _new_stage(self):
        self._stage_index += 1
        self._deal_board(self.NUMBER_OF_CARDS[self._stage_index])
        print(f"The board: {self.board}, the pot: {self.pot}")
        for player in self._active_players:
            player.new_stage()
        if self._stage_index == 1:
            for i in range(2):
                amount = self.blind_size / 2 * (1 + i)
                self._active_players[i].post_blind(amount)
                print(self._active_players[i].get_status())
            self._bets_round(self.players[1])
        else:
            self._bets_round()
        if self._number_of_players_left == 1 or self._stage_index == 4:
            if not self.winners:
                self._end()
        else:
            self._new_stage()

    @property
    def _active_players(self):
        return [player for player in self.players if player.is_active]

    @property
    def _number_of_players_left(self):
        return len(self._active_players)

    @property
    def max_bet(self):
        return max(player.get_bet for player in self.players)

    def _update_queue(self, last_raiser: Player):
        try:
            index = self._active_players.index(last_raiser)
        except ValueError:
            index = 0
        return self._active_players[index + 1:] + self._active_players[:index + 1]

    def _turns_queue(self, last_raiser: Player) -> Iterable[Player]:
        while not_decided := [player for player in self._update_queue(last_raiser) if not player.made_decision]:
            if len([player for player in self._active_players if not player.is_all_in]) == 1 and not self.max_bet:
                break
            yield not_decided[0]

    def _bets_round(self, last_raiser: Player = None):
        for player in self._active_players:
            if player is not last_raiser and not player.is_all_in:
                player.reset_decision()
        try:
            last_raiser: Player = last_raiser or self._active_players[0]
        except IndexError as e:
            print(self._active_players)
            raise e
        for player in self._turns_queue(last_raiser):
            current_max_bet = self.max_bet
            player.ask_for_a_decision(current_max_bet)
            if player.is_ai:
                # print('AI is thinking')
                if self._stage_index == 1:
                    decider = PreFlopDecider(player)
                    ai_decisions = decider.decision()
                    try:
                        decision = [d for d in ai_decisions if d in player.available_decisions][0]
                    except IndexError:
                        print(f"Something went wrong")
                        print(f"Player's available decisions: {player.available_decisions}")
                        print(f"AI's suggested decisions: {ai_decisions}")
                        raise UnavailableDecision
                    amount = decider.how_much_to_bet(self.blind_size, current_max_bet)
                    try:
                        player.decide(decision, amount)
                    except TooSmallBetError as e:
                        print(f"{self.max_bet=}, {player.stack=}, "
                              f"{player.requested_bet=}, {player.available_decisions=}, "
                              f"{player.get_bet=}, {decision=}, {amount=}")
                        raise e
                else:
                    decider = StageBetAI(self.board, player, self.blind_size, self._number_of_players_left)
                    ai_decisions = decider.should_i_bet(current_max_bet)
                    try:
                        decision = [d for d in ai_decisions if d in player.available_decisions][0]
                    except IndexError:
                        print(f"Something went wrong")
                        print(f"Player's available decisions: {player.available_decisions}")
                        print(f"AI's suggested decisions: {ai_decisions}")
                        raise UnavailableDecision
                    player.decide(decision, decider.how_much_to_bet(current_max_bet))
                print(player.get_status())
            else:
                console_input(player, self._board, current_max_bet)
            # while not player.made_decision:
            #     time.sleep(1)
            #     todo: add a timeout
            if player.get_bet > current_max_bet:
                last_raiser = player
                self._bets_round(last_raiser)
                return
        self._update_bank()
        if self._number_of_players_left == 1 and not self.winners:
            self._end()

    def _deal_players_cards(self):
        """just deal cards starting from the next after dealer"""
        for player in self.players:
            player.new_game_round()
        for _ in range(2):
            for player in self._active_players:
                player.add_card(self.deck.draw_one())
        self._new_stage()

    def _update_bank(self):
        self.pot += sum([player.get_bet for player in self.players])
        for player in self.players:
            player.new_stage()

    def _find_winners(self):
        print(f"current_players: {self.players}, pot: {self.pot}")
        if self._number_of_players_left == 1:
            self.winners = [self._active_players[0]]
            return
        else:
            self._stage_index += 1
            show_downs = tuple(player.show_down() for player in self._active_players)
            players_combs: list[tuple[int, tuple[Combination, tuple]]] = \
                list(enumerate(best_hand(sd + self.board) for sd in show_downs))
            combinations = sorted(players_combs, key=itemgetter(1), reverse=True)
            winners = []
            for i, comb in players_combs:
                if comb == combinations[0][1]:
                    winners.append(self._active_players[i])
            self.winners = winners

    def _calculate_prize(self):
        # todo add logic for bets over someone's all-in
        if len(self.winners) <= 1:
            return self.pot
        else:
            return self.pot / len(self.winners)

    def _end(self):
        self._find_winners()
        prize = self._calculate_prize()
        for winner in self.winners:
            winner.add_money(prize)
        print(self.get_status())
        # self.close_round()
        # for player in self.players:
        #     player.next_game_round()

    def close_round(self):
        for player in self.players:
            player.new_game_round()
        self.pot = 0

    def get_status(self):
        """return current game stage, players statuses, the bank and the table"""
        return {
            'stage': self.STAGES[self._stage_index],
            'board': self.board,
            'players': [player.get_status() for player in self.players]
        }
