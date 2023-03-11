from secrets import SystemRandom

import pytest

from ai.ai import all_possible_sets_to_open
from cards import Deck

secure_random = SystemRandom()


@pytest.mark.parametrize(
    'number_of_known, expected',
    [
        (7, 0),
        (6, 46),
        (5, 1081),
        (4, 17296),
        (3, 211876)
    ]
)
def test_unopened_count(number_of_known: int, expected: int):
    known_cards = tuple(secure_random.sample(list(Deck.all_cards()), number_of_known))
    assert len(all_possible_sets_to_open(known_cards)) == expected, \
        f'wrong amount of sets for {number_of_known} cards. Expected: {expected}'
