class Delta(dict):

    def __call__(self, var):
        from lambdac import Var, LambdaExpr
        assert isinstance(var, Var)
        return self.get(var, var)

    def __str__(self):
        replacements = ', '.join(['{} → {}'.format(k, v) for k, v in self.items()])
        return 'Delta({})'.format(replacements)

    def __setitem__(self, k, v):
        from lambdac import Var, LambdaExpr
        assert isinstance(k, Var)
        assert isinstance(v, LambdaExpr)
        super().__setitem__(k, v)

    def __repr__(self):
        return str(self)
