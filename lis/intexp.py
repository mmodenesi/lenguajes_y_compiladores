import re

from expr import Expr
from operators import BinOP, OP


class IntExp(Expr):
    pass


class Const(IntExp):
    def __init__(self, n):
        self.n = n

    def _sem(self, state):
        return self.n

    def __str__(self):
        if self.n < 0:
            return '({})'.format(self.n)
        else:
            return str(self.n)

    def _replace(self, delta, strict):
        return Const(self.n)


class Var(IntExp):
    def __init__(self, name):
        assert isinstance(name, str)
        self._name = name

        match = re.search(r'(.*)(\d+)$', name)
        if match:
            self._name, i = match.groups()
            self._number = int(i)
        else:
            self._name = name
            self._number = 0

    def __hash__(self):
        return hash(self.name)

    def __iter__(self):
        return self

    def __next__(self):
        return Var('{}{}'.format(self._name, self._number + 1))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name

    def __str__(self):
        return self.name

    def _sem(self, state):
        return state[self]

    def _replace(self, delta, strict):
        return delta(self, strict)

    @property
    def name(self):
        return '{}{}'.format(self._name, self._number if self._number > 0 else '')

    def fv(self):
        return {self}


class Mul(BinOP, IntExp):
    OP_STR = '*'
    OPERATOR = lambda x, y: x * y


class Plus(BinOP, IntExp):
    OP_STR = '+'
    OPERATOR = lambda x, y: x + y


class Div(BinOP, IntExp):
    OP_STR = '/'
    OPERATOR = lambda x, y: 0 if y == 0 else x // y


class Mod(BinOP, IntExp):
    OP_STR = '%'
    OPERATOR = lambda x, y: 0 if y == 0 else x % y


class Neg(OP, IntExp):
    OP_STR = '-'
    OPERATOR = lambda x: -x
