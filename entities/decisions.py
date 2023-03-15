# todo implement decisions or redo them as enum.
"""
Decisions must be usable as a game action and readable in an action history
The main property(for raise and all-in) is the bet size.
Should it be done as ENUM?
"""


class Decision:
    pass


class Fold(Decision):
    pass


class Check(Decision):
    pass


class Call(Decision):
    pass


class Raise(Decision):
    pass
