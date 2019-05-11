from expr import Expr
from intexp import Var
from operators import BinOP, OP
from replace import Delta


class BoolExp(Expr):
    def _sem(self, state):
        raise NotImplementedError('No semantics for {}'.format(self))


class Implies(BinOP, BoolExp):
    OP_STR = '⇒'
    OPERATOR = lambda x, y: not x or y


class Eq(BinOP, BoolExp):
    OP_STR = '='
    OPERATOR = lambda x, y: x == y


class Gt(BinOP, BoolExp):
    OP_STR = '>'
    OPERATOR = lambda x, y: x > y


class Geq(BinOP, BoolExp):
    OP_STR = '≥'
    OPERATOR = lambda x, y: x >= y


class Lt(BinOP, BoolExp):
    OP_STR = '<'
    OPERATOR = lambda x, y: x < y


class Leq(BinOP, BoolExp):
    OP_STR = '≤'
    OPERATOR = lambda x, y: x <= y


class Or(BinOP, BoolExp):
    OP_STR = '∨'
    OPERATOR = lambda x, y: x or y


class And(BinOP, BoolExp):
    OP_STR = '∧'
    OPERATOR = lambda x, y: x and y


class Lnot(OP, BoolExp):
    OP_STR = '¬'
    OPERATOR = lambda x: not x


class Q(BoolExp):
    def __init__(self, binding, reach):
        assert isinstance(binding, Var)
        assert isinstance(reach, BoolExp)
        self.binding = binding
        self.reach = reach

    def __str__(self):
        return '{}{}.{}'.format(self.OP_STR, self.binding, self.reach)

    def fv(self):
        return self.reach.fv() - {self.binding}

    def _replace(self, delta, strict):
        forbidden = set(sum((list(delta(w).fv()) for w in self.fv()), []))
        vnew = self.binding

        while vnew in forbidden:
            vnew = next(vnew)

        newdelta = Delta(delta)
        newdelta[self.binding] = vnew

        return self.__class__(vnew, self.reach.replace(newdelta, strict))


class All(Q):
    OP_STR = '∀'


class Exists(Q):
    OP_STR = '∃'
