from functools import cache, reduce
from math import factorial


@cache
def n_choose_k(n: int, k: int) -> int:
    """N choose K with reduced factorial"""
    return reduce(lambda x, y: x * y, [n - _k for _k in range(k)]) // factorial(k)
