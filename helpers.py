from functools import cache, reduce
from math import factorial


@cache
def n_choose_k(n: int, k: int) -> int:
    return reduce(lambda x, y: x * y, [n - _k for _k in range(k)]) // factorial(k)
