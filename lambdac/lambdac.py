import re

from replace import Delta


class LambdaExpr:

    def __repr__(self):
        return str(self)

    def is_redex(self):
        return False

    def is_closed(self):
        return not self.fv()


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
        types = type(self.operator), type(self.operand)
        if types == (Abstraction, Abstraction):
            template = '({})({})'
        elif types == (Abstraction, Application):
            template = '({})({})'
        elif types == (Abstraction, Var):
            template = '({}){}'
        elif types == (Application, Abstraction):
            template = '({})({})'
        elif types == (Application, Application):
            template = '({})({})'
        elif types == (Application, Var):
            template = '({}){}'
        elif types == (Var, Var):
            template = '{}{}'
        elif types == (Var, Abstraction):
            template = '{}({})'
        elif types == (Var, Application):
            template = '{}({})'

        return template.format(self.operator, self.operand)

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


def lambda_reduce(expr, verbose=False):
    """Take expr to a normal form."""

    def inner(expr, verbose):
        if type(expr) == Var:
            return expr
        if type(expr) == Application:
            operand = expr.operand
            operator = expr.operator
            if expr.is_redex():
                delta = Delta({operator.bind: operand})
                new_expr = operator.reach.replace(delta)
                if verbose:
                    print('{} → {}'.format(expr, new_expr))
                return inner(new_expr, verbose)
            else:
                result = Application(inner(operator, verbose), inner(operand, verbose))
                if result.is_redex():
                    return inner(result, verbose)
                else:
                    return result
        if type(expr) == Abstraction:
            return Abstraction(expr.bind, inner(expr.reach, verbose))

    try:
        return inner(expr, verbose)
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

        # abstracions are the cannonical form
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
