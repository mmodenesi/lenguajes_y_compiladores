import re

from replace import Delta


class LambdaExpr:

    def is_redex(self):
        return False

    def is_closed(self):
        return not self.fv()

    def replace(self, delta):
        return self

    def fv(self):
        return set()


class Var(LambdaExpr):

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

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, self.name)

    def is_normal_form(self):
        return True

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

    def replace(self, delta):
        return delta(self)

    @property
    def name(self):
        return '{}{}'.format(self._name, self._number if self._number > 0 else '')

    def fv(self):
        return {self}


class Application(LambdaExpr):
    def __init__(self, operator, operand):
        assert isinstance(operator, LambdaExpr)
        assert isinstance(operand, LambdaExpr)
        self.operator = operator
        self.operand = operand

    def is_redex(self):
        return type(self.operator) == Abstraction

    def is_normal_form(self):
        if self.is_redex():
            return False
        return self.operator.is_normal_form() and self.operand.is_normal_form()

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.operator == other.operator and self.operand == other.operand

    def __str__(self):
        template = '({})({})'
        return template.format(self.operator, self.operand)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   repr(self.operator),
                                   repr(self.operand))

    def replace(self, delta):
        return Application(self.operator.replace(delta), self.operand.replace(delta))

    def fv(self):
        return self.operator.fv() | self.operand.fv()


class Abstraction(LambdaExpr):
    def __init__(self, bind, reach):
        assert isinstance(bind, Var)
        assert isinstance(reach, LambdaExpr), 'got {} instead'.format(type(LambdaExpr))
        self.bind = bind
        self.reach = reach

    def __str__(self):
        return 'λ{}.{}'.format(self.bind, self.reach)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   repr(self.bind),
                                   repr(self.reach))

    def rename(self, newbind):
        if newbind in (self.reach.fv() - {self.bind}):
            raise ValueError('{} is free in {}'.format(newbind, self.reach))
        return Abstraction(newbind, self.reach.replace(Delta({self.bind: newbind})))

    def fv(self):
        return self.reach.fv() - {self.bind}

    def replace(self, delta):
        forbidden = set(sum((list(delta(w).fv()) for w in self.fv()), []))
        vnew = self.bind

        while vnew in forbidden:
            vnew = next(vnew)

        newdelta = Delta(delta)
        newdelta[self.bind] = vnew

        return Abstraction(vnew, self.reach.replace(newdelta))

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.reach == other.reach.replace(Delta({other.bind: self.bind}))

    def is_normal_form(self):
        return self.reach.is_normal_form()


def get_path_to_outermost_leftmost_redex(expr, path=''):
    if type(expr) == Var:
        return None
    if type(expr) == Abstraction:
        return get_path_to_outermost_leftmost_redex(expr.reach, path + '.reach')
    if type(expr) == Application:
        if expr.is_redex():
            return path
        left = get_path_to_outermost_leftmost_redex(expr.operator, path + '.operator')
        right = get_path_to_outermost_leftmost_redex(expr.operand, path + '.operand')
        if left is not None and right is not None:
            if len(left.split('.')) >= len(right.split('.')):
                return left
            return right
        elif left is not None:
            return left
        return right
    assert False


def lambda_reduce(expr, verbose=False):
    """Take expr to a normal form."""

    def inner(expr):
        if verbose:
            print(expr)
        while True:
            path = get_path_to_outermost_leftmost_redex(expr)
            if path is None:
                break
            redex = eval('expr{}'.format(path))
            delta = Delta({redex.operator.bind: redex.operand})
            beta_contraction = redex.operator.reach.replace(delta)
            path = path.split('.')[1:]
            elem = expr
            while len(path) > 1:
                attr = path.pop(0)
                elem = getattr(elem, attr)
            if path:
                setattr(elem, path[0], beta_contraction)
            else:
                expr = beta_contraction
            if verbose:
                print('→', expr)
        return expr

    try:
        return inner(expr)
    except RecursionError as e:
        print(e)


def normal_evaluation(expr, verbose=False):
    """Perform normal evaluation on expr."""

    if not expr.is_closed():
        raise ValueError('Only closed expresions may be evaluated')

    def inner(expr, branch_id=None):
        branch_id = branch_id or []

        def maybe_print(msg):
            if verbose:
                print('{} {}'.format('.'.join(branch_id), msg))

        # abstractions are the cannonical form
        if type(expr) == Abstraction:
            maybe_print('{} ⇒ {}'.format(expr, expr))
            result = expr
        else:
            # expr is Application
            maybe_print(expr)

            e = inner(expr.operator, branch_id + ['a'])
            z = e.reach.replace(Delta({e.bind: expr.operand}))

            result = inner(z, branch_id + ['b'])
            maybe_print('⇒ {}'.format(result))

        return result

    try:
        return inner(expr)
    except RecursionError as e:
        print(e)


def eager_evaluation(expr, verbose=False):
    """Perform eager evaluation on expr."""
    from extensions import If, NatConst, BoolConst, BinOP, OP, Tuple, TupleAt, Letrec

    if not expr.is_closed():
        raise ValueError('Only closed expresions may be evaluated')

    def inner(expr, branch_id=None):
        branch_id = branch_id or []

        def maybe_print(msg):
            if verbose:
                if branch_id:
                    print('{} {}'.format('.'.join(branch_id), msg))
                else:
                    print(msg)

        maybe_print(expr)
        if type(expr) == Abstraction:
            result = expr
        elif type(expr) == Application:
            e1 = inner(expr.operator, branch_id + ['a'])
            z1 = inner(expr.operand, branch_id + ['b'])
            z = e1.reach.replace(Delta({e1.bind: z1}))
            result = inner(z, branch_id + ['c'])
        elif type(expr) == If:
            guard = inner(expr.b, branch_id + ['a'])
            assert isinstance(guard, BoolConst)
            if guard.value():
                result = inner(expr.e1, branch_id + ['b'])
            else:
                result = inner(expr.e2, branch_id + ['b'])
        elif type(expr) in (NatConst, BoolConst):
            result = expr
        elif issubclass(expr.__class__, BinOP):
            a = inner(expr.a, branch_id + ['a'])
            b = inner(expr.b, branch_id + ['b'])
            value = getattr(expr.__class__, 'OPERATOR')(a.value(), b.value())
            if type(value) == int:
                result = NatConst(value)
            else:
                result = BoolConst(value)
        elif issubclass(expr.__class__, OP):
            a = inner(expr.a, branch_id + ['a'])
            value = getattr(expr.__class__, 'OPERATOR')(a.value())
            if type(value) == int:
                result = NatConst(value)
            else:
                result = BoolConst(value)
        elif type(expr) == Tuple:
            index = 'a'
            canonic_forms = []
            for index, elem in enumerate(expr.elems, ord('a')):
                canonic_forms.append(inner(elem, branch_id + [chr(index)]))
            result = Tuple(*canonic_forms)
        elif type(expr) == TupleAt:
            result = inner(expr.t, branch_id + ['a']).elems[expr.k - 1]
        elif type(expr) == Letrec:
            abstraction = Abstraction(
                expr.e1.bind,
                Letrec(expr.v, expr.e1, expr.e1.reach))
            delta = Delta({expr.v: abstraction})
            new_expr = expr.e2.replace(delta)
            result = inner(new_expr, branch_id + ['a'])
        else:
            assert False, repr(expr)

        maybe_print('⇒ {}'.format(result))
        return result

    try:
        return inner(expr)
    except RecursionError as e:
        print(e)
