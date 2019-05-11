class BinOP:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def _sem(self, state):
        return getattr(self.__class__, 'OPERATOR')(self.a.sem(state), self.b.sem(state))

    def __str__(self):
        return '({} {} {})'.format(self.a, self.OP_STR, self.b)

    def fv(self):
        return self.a.fv() | self.b.fv()

    def _replace(self, delta, strict):
        return self.__class__(self.a.replace(delta, strict), self.b.replace(delta, strict))


class OP:
    def __init__(self, a):
        self.a = a

    def _sem(self):
        return getattr(self.__class__, 'OPERATOR')(self.a.sem(state))

    def __str__(self):
        return '({} {})'.format(self.OP_STR, self.a)

    def fv(self):
        return self.a.fv()

    def replace(self, delta, strict):
        return self.__class__(self.a.replace(delta, strict))
