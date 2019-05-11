from expr import Expr
from intexp import Const, Var, IntExp
from replace import Delta


class Comm(Expr):

    def fa(self):
        return set()


class Skip(Comm):
    def _sem(self, state):
        return state

    def __str__(self):
        return 'skip'

    def _replace(self, delta, strict):
        return Skip()


class Assign(Comm):
    def __init__(self, var, intexp):
        assert isinstance(var, Var)
        assert isinstance(intexp, IntExp)
        self.var = var
        self.intexp = intexp

    def _sem(self, state):
        state[self.var] = self.intexp.sem(state)
        return state

    def __str__(self):
        return '{} := {}'.format(self.var.name, self.intexp)

    def fv(self):
        return {self.var} | self.intexp.fv()

    def fa(self):
        return {self.var}

    def _replace(self, delta, strict):
        return Assign(self.var.replace(delta, strict=True), self.intexp.replace(delta, strict=True))


class Concat(Comm):
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1

    def _sem(self, state):
        return self.c1.sem(self.c0.sem(state))

    def __str__(self):
        return '({}; {})'.format(self.c0, self.c1)

    def fv(self):
        return self.c0.fv() | self.c1.fv()

    def fa(self):
        return self.c0.fa() | self.c1.fa()

    def _replace(self, delta, strict):
        return Concat(self.c0.replace(delta, strict=True), self.c1.replace(delta, strict=True))


class If(Comm):
    def __init__(self, b, c0, c1):
        self.b = b
        self.c0 = c0
        self.c1 = c1

    def _sem(self, state):
        if self.b.sem(state):
            return self.c0.sem(state)
        else:
            return self.c1.sem(state)

    def __str__(self):
        return 'if {} then {} else {}'.format(self.b, self.c0, self.c1)

    def fv(self):
        return self.b.fv() | self.c0.fv() | self.c1.fv()

    def fa(self):
        return self.c0.fa() | self.c1.fa()

    def _replace(self, delta, strict):
        return If(self.b.replace(delta, strict=True),
                  self.c0.replace(delta, strict=True),
                  self.c1.replace(delta, strict=True))


class While(Comm):
    def __init__(self, b, c):
        self.b = b
        self.c = c

    def _sem(self, state):
        while self.b.sem(state):
            state = self.c.sem(state)
        return state

    def __str__(self):
        return 'while {} do {}'.format(self.b, self.c)

    def fv(self):
        return self.b.fv() | self.c.fv()

    def fa(self):
        return self.c.fa()

    def _replace(self, delta, strict):
        return While(self.b.replace(delta, strict=True), self.c.replace(delta, strict=True))


class NewVar(Comm):
    def __init__(self, var, intexp, c):
        assert isinstance(var, Var)
        self.var = var
        self.intexp = intexp
        self.c = c

    def _sem(self, state):
        try:
            oldvalue = self.var.sem(state)
        except NameError:
            oldvalue = None
        state = Assign(self.var, self.intexp).sem(state)
        state = self.c.sem(state)

        if oldvalue is not None:
            return Assign(self.var, Const(oldvalue)).sem(state)
        else:
            state.pop(self.var)
            return state

    def __str__(self):
        return 'newvar {} := {} in {}'.format(self.var, self.intexp, self.c)

    def fv(self):
        return self.intexp.fv() | (self.c.fv() - {self.var})

    def fa(self):
        return self.c.fa() - {self.var}

    def _replace(self, delta, strict):
        forbidden = set([delta(w) for w in self.c.fv() - {self.var}])
        vnew = self.var
        while vnew in forbidden:
            vnew = next(vnew)

        newdelta = Delta(delta)
        newdelta[self.var] = vnew

        return NewVar(vnew,
                      self.intexp.replace(delta, strict=True),
                      self.c.replace(newdelta, strict=True))
