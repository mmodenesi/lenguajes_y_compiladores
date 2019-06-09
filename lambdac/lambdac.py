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

    def _maybe_print(self, msg, verbose, branch_id):
        if verbose:
            if branch_id:
                print('{} {}'.format('.'.join(branch_id), msg))
            else:
                print(msg)

    def eval(self, strategy, verbose, branch_id):
        if not self.is_closed():
            raise ValueError('{} is not a closed expresions'.format(self))
        if strategy not in ('eager', 'normal'):
            raise ValueError('"{}" is not an evaluation strategy'.format(strategy))

        branch_id = branch_id or []
        self._maybe_print(str(self), verbose, branch_id)

        diverges = False
        result = self._eval(strategy, verbose, branch_id)
        self._maybe_print('⇒ {}'.format(result), verbose, branch_id)
        return result

    def normal_eval(self, verbose=False, branch_id=None):
        return self.eval('normal', verbose, branch_id)

    def eager_eval(self, verbose=False, branch_id=None):
        return self.eval('eager', verbose, branch_id)


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

    def _eval(self, strategy, verbose, branch_id):
        if strategy == 'eager':
            e1 = self.operator.eval(strategy, verbose, branch_id + ['a'])
            z1 = self.operand.eval(strategy, verbose, branch_id + ['b'])
            z = e1.reach.replace(Delta({e1.bind: z1}))
            return z.eval(strategy, verbose, branch_id + ['c'])
        else:
            e = self.operator.eval(strategy, verbose, branch_id + ['a'])
            z = e.reach.replace(Delta({e.bind: self.operand}))
            return z.eval(strategy, verbose, branch_id + ['b'])


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

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.reach == other.reach.replace(Delta({other.bind: self.bind}))

    def _eval(self, strategy, verbose, branch_id):
        return self

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
