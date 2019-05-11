from state import State


class Expr:
    def sem(self, state):
        msg = '{}.sem got {} instead of State'.format(self.__class__.__name__, type(state))
        assert isinstance(state, State), msg
        return self._sem(state.copy())

    def replace(self, delta, strict=False):
        from replace import Delta
        msg = '{}.replace got {} instead of Delta'.format(self.__class__.__name__, type(delta))
        assert isinstance(delta, Delta), msg
        return self._replace(delta, strict=strict)

    def __repr__(self):
        return str(self)

    def fv(self):
        return set()
