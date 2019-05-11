class State:
    def __init__(self, mapping=None, **kwargs):
        self._dict = dict()
        if mapping is not None:
            for key, value in mapping.items():
                self[key] = value

            for key, value in kwargs.items():
                self[key] = value

    def __getitem__(self, var):
        from intexp import Var
        msg = 'State got {} instead of Var'.format(type(var))
        assert isinstance(var, Var), msg
        if not var in self._dict:
            raise NameError('unbound variable "{}"'.format(var))
        return self._dict[var]

    def __setitem__(self, var, value):
        from intexp import Var
        msg = 'State.__setitem__ got var of type {} instead of Var'.format(type(var))
        assert isinstance(var, Var), msg
        msg = 'State.__setitem__ got value of type {} instead of int'.format(type(value))
        assert isinstance(value, int), msg
        self._dict[var] = value

    def pop(self, var):
        return self._dict.pop(var)

    def copy(self):
        return State(self._dict.copy())

    def __str__(self):
        return str(self._dict)

    def __repr__(self):
        return str(self)


def state_factory(names, values):
    assert(len(names) == len(values))
    assert all(isinstance(s, str) for s in names)
    assert all(isinstance(i, int) for i in values)
    from intexp import Var
    return State(dict(zip(map(Var, names), values)))
