from intexp import Var, IntExp


class Delta(dict):

    def __call__(self, var, strict=False):
        assert isinstance(var, Var)
        result = self.get(var, var)
        if strict:
            assert isinstance(result, Var), 'Can not replace Var with IntExp'
        return result

    def __str__(self):
        replacements = ', '.join(['{} → {}'.format(k, v) for k, v in self.items()])
        return 'Delta({})'.format(replacements)

    def __setitem__(self, k, v):
        assert isinstance(k, Var)
        assert isinstance(v, IntExp)
        super().__setitem__(k, v)

    def __repr__(self):
        return str(self)
