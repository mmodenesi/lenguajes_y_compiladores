from functools import reduce
from comm import Concat


def concat(commands):
    return reduce(lambda x, y: Concat(x, y), commands)
