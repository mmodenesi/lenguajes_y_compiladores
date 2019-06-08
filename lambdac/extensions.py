from lambdac import *
from replace import Delta


class BinOP:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self):
        return '({} {} {})'.format(self.a, self.OP_STR, self.b)

    @classmethod
    def _operate(cls, a, b):
        return cls.OPERATOR(a, b)

    def fv(self):
        return self.a.fv() | self.b.fv()

    def replace(self, delta):
        return self.__class__(self.a.replace(delta), self.b.replace(delta))

    def _eval(self, strategy, verbose, branch_id):
        if strategy == 'eager':
            a = self.a.eval(strategy, verbose, branch_id + ['a'])
            b = self.b.eval(strategy, verbose, branch_id + ['b'])
            value = self._operate(a.value(), b.value())
        else:
            a = self.a.eval(strategy, verbose, branch_id + ['a'])
            a_val = a.value()

            if isinstance(self, Or):
                if a_val:
                    value = True
                else:
                    value = self.b.eval(strategy, verbose, branch_id + ['b'])

            elif isinstance(self, And):
                if not a_val:
                    value = False
                else:
                    value = self.b.eval(strategy, verbose, branch_id + ['b'])

            elif isinstance(self, Implies):
                if a_val:
                    value = self.b.eval(strategy, verbose, branch_id + ['b'])
                else:
                    value = True
            else:
                b = self.b.eval(strategy, verbose, branch_id + ['b'])
                value = self._operate(a_val, b.value())

            if isinstance(value, int):
                return NatConst(value)
            return BoolConst(value)


class OP:
    def __init__(self, a):
        self.a = a

    def __str__(self):
        return '({} {})'.format(self.OP_STR, self.a)

    @classmethod
    def _operate(cls, value):
        return cls.OPERATOR(vale)

    def fv(self):
        return self.a.fv()

    def replace(self, delta):
        return self.__class__(self.a.replace)

    def _eval(self, strategy, verbose, branch_id):
        a = self.a.eval(strategy, verbose, branch_id + ['a'])
        value = self._operate(a.value())
        if type(value) == int:
            return NatConst(value)
        return BoolConst(value)


class NatConst(LambdaExpr):
    def __init__(self, n):
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.n)

    def value(self):
        return self.n

    def _eval(self, strategy, verbose, branch_id):
        return self


class BoolConst(NatConst):
    pass


class Implies(BinOP, BoolConst):
    OP_STR = '⇒'
    OPERATOR = lambda x, y: not x or y


class Eq(BinOP, BoolConst):
    OP_STR = '='
    OPERATOR = lambda x, y: x == y


class Gt(BinOP, BoolConst):
    OP_STR = '>'
    OPERATOR = lambda x, y: x > y


class Geq(BinOP, BoolConst):
    OP_STR = '≥'
    OPERATOR = lambda x, y: x >= y


class Lt(BinOP, BoolConst):
    OP_STR = '<'
    OPERATOR = lambda x, y: x < y


class Leq(BinOP, BoolConst):
    OP_STR = '≤'
    OPERATOR = lambda x, y: x <= y


class Or(BinOP, BoolConst):
    OP_STR = '∨'
    OPERATOR = lambda x, y: x or y


class And(BinOP, BoolConst):
    OP_STR = '∧'
    OPERATOR = lambda x, y: x and y


class Lnot(OP, BoolConst):
    OP_STR = '¬'
    OPERATOR = lambda x: not x


class Mul(BinOP, NatConst):
    OP_STR = '*'
    OPERATOR = lambda x, y: x * y


class Plus(BinOP, NatConst):
    OP_STR = '+'
    OPERATOR = lambda x, y: x + y


class Div(BinOP, NatConst):
    OP_STR = '/'
    OPERATOR = lambda x, y: 0 if y == 0 else x // y


class Mod(BinOP, NatConst):
    OP_STR = '%'
    OPERATOR = lambda x, y: 0 if y == 0 else x % y


class Neg(OP, NatConst):
    OP_STR = '-'
    OPERATOR = lambda x: -x


class If(LambdaExpr):
    def __init__(self, b, e1, e2):
        self.b = b
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return '{}({}, {}, {})'.format(
                self.__class__.__name__, repr(self.b), repr(self.e1), repr(self.e2))

    def __str__(self):
        return 'if {} then {} else {}'.format(self.b, self.e1, self.e2)

    def _eval(self, strategy, verbose, branch_id):
        guard = self.b.eval(strategy, verbose, branch_id + ['a'])
        assert isinstance(guard, BoolConst)
        if guard.value():
            return self.e1.eval(strategy, verbose, branch_id + ['b'])
        return self.e2.eval(strategy, verbose, branch_id + ['b'])

    def fv(self):
        return self.b.fv() | self.e1.fv() | self.e2.fv()

    def replace(self, delta):
        return self.__class__(
                self.b.replace(delta),
                self.e1.replace(delta),
                self.e2.replace(delta))

class Tuple(LambdaExpr):
    def __init__(self, *args):
        self.elems = args

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ','.join((repr(e) for e in self.elems)))

    def __str__(self):
        return '〈{}〉'.format(', '.join((str(e) for e in self.elems)))

    def _eval(self, strategy, verbose, branch_id):
        if strategy == 'eager':
            canonic_forms = []
            for index, elem in enumerate(self.elems, ord('a')):
                canonic_forms.append(elem.eager_eval(verbose, branch_id + [chr(index)]))
            return Tuple(*canonic_forms)
        else:
            return self

    def fv(self):
        result = set()
        for e in self.elems:
            result |= e.fv()
        return result

    def replace(self, delta):
        return self.__class__(*[e.replace(delta) for e in self.elems])


class TupleAt(LambdaExpr):
    def __init__(self, t, k):
        self.t = t
        self.k = k

    def __repr__(self):
        return '{}({}, {})'.format(
            self.__class__.__name__, repr(self.t), self.k)

    def __str__(self):
        return '{}.{}'.format(self.t, self.k)

    def _eval(self, strategy, verbose, branch_id):
        if strategy == 'eager':
            return self.t.eval(strategy, verbose, branch_id + ['a']).elems[self.k - 1]
        else:
            return self.t[self.k - 1].eval(strategy, verbose, branch_id + ['a'])

    def fv(self):
        return self.t.fv()


class Letrec(LambdaExpr):
    def __init__(self, v, e1, e2):
        self.v = v
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return 'Letrec({}, {}, {})'.format(repr(self.v), repr(self.e1), repr(self.e2))

    def __str__(self):
        return 'letrec {} ≡ {} in {}'.format(self.v, self.e1, self.e2)

    def fv(self):
        return (self.e1.fv() | self.e2.fv()) - {self.v}

    def replace(self, delta):
        forbidden = set(sum((list(delta(w).fv()) for w in self.fv()), []))
        vnew = self.v

        while vnew in forbidden:
            vnew = next(vnew)

        newdelta = Delta(delta)
        newdelta[self.v] = vnew

        return Letrec(vnew, self.e1.replace(newdelta), self.e2.replace(newdelta))

    def _eval(self, strategy, verbose, branch_id):
        if strategy == 'eager':
            abstraction = Abstraction(
                self.e1.bind,
                Letrec(self.v, self.e1, self.e1.reach))
            delta = Delta({self.v: abstraction})
            new_expr = self.e2.replace(delta)
            return new_expr.eager_eval(verbose, branch_id + ['a'])
