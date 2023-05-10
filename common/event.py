from collections import defaultdict
from enum import Enum, auto
from typing import Callable


class EventType(Enum):
    """Store all possible types of events"""
    PLAYER_PREPARE_MOVE = auto()  # noqa
    PLAYER_MAKE_MOVE = auto()  # noqa
    PLAYER_MOVED = auto()  # noqa
    NEW_STAGE = auto()  # noqa
    WINNERS_CALCULATED = auto()  # noqa
    ROUND_END = auto()  # noqa


subscribers = defaultdict(list)


def subscribe(event_type: EventType, fn: Callable):
    """Add a function that would be called on event"""
    subscribers[event_type].append(fn)


def post_event(event_type: EventType, *args, **kwargs):
    """Call all the functions associated with the posted event"""
    if event_type not in subscribers:
        return
    for fn in subscribers[event_type]:
        fn(*args, **kwargs)


if __name__ == '__main__':
    pass
