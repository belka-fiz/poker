from dataclasses import dataclass, field
from random import shuffle


@dataclass(repr=False)
class Suit:
    """Card suit"""

    short_name: str
    long_name: str

    def __repr__(self):
        return self.short_name

    def __str__(self):
        return self.short_name

    def __hash__(self):
        return hash(self.short_name)


@dataclass(eq=True, order=True)
class Value:
    """
    Card value.
    Values are comparable by the order
    """

    order: int
    name: str = field(compare=False)
    short_name: str = field(compare=False)

    def __repr__(self):
        return self.short_name

    def __hash__(self):
        return hash(self.short_name)


SUITS = (
    Suit('d', 'Diamonds'),
    Suit('s', 'Spades'),
    Suit('h', 'Hearts'),
    Suit('c', 'Clubs')
)

VALUES = (
    Value(2, 'Two', '2'),
    Value(3, 'Three', '3'),
    Value(4, 'Four', '4'),
    Value(5, 'Five', '5'),
    Value(6, 'Six', '6'),
    Value(7, 'Seven', '7'),
    Value(8, 'Eight', '8'),
    Value(9, 'Nine', '9'),
    Value(10, 'Ten', 'T'),
    Value(11, 'Jack', 'J'),
    Value(12, 'Queen', 'Q'),
    Value(13, 'King', 'K'),
    Value(14, 'Ace', 'A')
)
ZERO_ACE: Value = Value(1, 'Ace', 'A')


@dataclass(order=True, eq=True)
class Card:
    """
    The card
    Cards are comparable by value and suit.
    Cards are equal if their values are equal
    """

    suit: Suit = field(hash=True, compare=False)
    value: Value

    def __str__(self):
        return self.value.short_name + self.suit.short_name

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.suit) + hash(self.value)


class Deck:
    """
    The Deck.
    Contains 52 cards and mixed in the beginning
    Cards are removed from the deck when dealt or hidden
    """

    __cards: tuple[Card] = tuple(Card(s, v) for s in SUITS for v in VALUES)

    def __init__(self):
        self._order = []
        self.mix()

    def mix(self) -> None:
        """Shuffle the deck"""
        self._order = list(self.__cards)
        shuffle(self._order)

    def draw_one(self) -> Card:
        """Deal a card to a player"""
        return self._order.pop()

    def hide_one(self) -> None:
        """Hide a card from the deck without giving it to anyone"""
        self._order.pop()

    @property
    def cards_left(self) -> int:
        """represents how many cards are left in the deck"""
        return len(self._order)

    @classmethod
    def all_cards(cls) -> set[Card]:
        """Return all possible cards in a deck"""
        return set(cls.__cards)
