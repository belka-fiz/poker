from secrets import SystemRandom
from time import time
from typing import Iterable

from ai.ai import possible_boards, all_possible_sets_to_open, possible_board_according_to_hand, possible_competitors_hands
from entities.cards import Card, Deck

random = SystemRandom()


# @cache
def several_competitors_hands(known_hands: frozenset[frozenset[Card]] = None,
                              competitors_num: int = 1) -> set[frozenset[frozenset[Card]]]:
    known_hands = known_hands or frozenset()
    known_cards = []
    for hand in known_hands:
        for card in hand:
            known_cards.append(card)
    first_competitors_cards = {frozenset([frozenset(hand)]) for hand in possible_competitors_hands(tuple(known_cards))}
    if competitors_num == 1:
        return first_competitors_cards
    else:
        result = set()
        for possible_opponents_hands in first_competitors_cards:
            for hand in possible_opponents_hands:
                _known_hands = known_hands | hand
            for _result in several_competitors_hands(frozenset([_known_hands]), competitors_num=competitors_num-1):
                result.add(possible_opponents_hands | _result)
        return result


def is_pair(hand: Iterable[Card]) -> bool:
    card1: Card
    card2: Card
    card1, card2 = hand
    return card1.value == card2.value


def is_suited(hand: Iterable[Card]) -> bool:
    card1: Card
    card2: Card
    card1, card2 = hand
    return card1.suit == card2.suit


def hands_calc():
    all_hands = possible_competitors_hands()
    all_pairs = [hand for hand in all_hands if is_pair(hand)]
    all_suited = [hand for hand in all_hands if is_suited(hand)]
    print(f"There are {len(all_hands)} possible hands. Pairs are {len(all_pairs)} of them,"
          f" which is {len(all_pairs)/len(all_hands)*100:.2f}%")
    print(f"There are {len(all_hands)} possible hands. Suited are {len(all_suited)} of them,"
          f" which is {len(all_suited)/len(all_hands)*100:.2f}%")
    my_random_hand = tuple(random.sample(sorted(Deck.all_cards()), 2))
    possible_cards = possible_competitors_hands(my_random_hand)
    possible_pairs = [hand for hand in possible_cards if is_pair(hand)]
    possible_suited = [hand for hand in possible_cards if is_suited(hand)]
    print(my_random_hand)
    print(f"There are {len(possible_cards)} possible hands. Pairs are {len(possible_pairs)} of them,"
          f" which is {len(possible_pairs)/len(possible_cards)*100:.2f}%")
    print(f"There are {len(possible_cards)} possible hands. Suited are {len(possible_suited)} of them,"
          f" which is {len(possible_suited)/len(possible_cards)*100:.2f}%")
    two_competitors_hands = several_hands()
    pairs = 0
    suited = 0
    for competitors in two_competitors_hands:
        for hand in competitors:
            if is_suited(hand):
                suited += 1
            elif is_pair(hand):
                pairs += 1
    print(f"If there are two competitors, we can find {pairs} pairs and {suited} suited hands\n"
          f"That are {pairs/len(two_competitors_hands)*100:.2f}% "
          f"and {suited/len(two_competitors_hands)*100:.2f}% of {len(two_competitors_hands)} respectively")
    print()


def time_comparison():
    deck = Deck()
    hand = tuple(deck.draw_one() for _ in range(2))
    second_hand = tuple(deck.draw_one() for _ in range(2))

    board = tuple(deck.draw_one() for _ in range(3))
    start = time()
    possible_boards(board)
    new = possible_board_according_to_hand(board, hand)
    second_new = possible_board_according_to_hand(board, second_hand)
    print(f'New variant took {time() - start:.4f} seconds')
    old_start = time()
    old = all_possible_sets_to_open(hand+board)
    second_old = all_possible_sets_to_open(second_hand+board)
    print(f'Old variant took {time() - old_start:.4f} seconds')
    print(new == old)
    print(second_new == second_old)


def several_hands(num: int = 2):
    deck = Deck()
    my_hand = frozenset(deck.draw_one() for _ in range(2))
    hands = my_hand,
    return several_competitors_hands(known_hands=frozenset(hands), competitors_num=num)


def main():
    start = time()
    # hands_calc()
    # time_comparison()
    # several_hands()
    print(f"The game took {(time()-start):.4f} seconds")


if __name__ == '__main__':
    main()
