from lambdac import *
from extensions import *


inner = Application(
            Abstraction(Var('f'), Tuple(NatConst(1), Application(Var('f'), Var('f')))),
            Abstraction(Var('f'), Tuple(NatConst(1), Application(Var('f'), Var('f')))),
        )

expr = TupleAt(Tuple(NatConst(1), inner), NatConst(1))

i = 0
while i < 10:
    new_expr = expr.normal_eval()
    print(expr, 'evaluates to', new_expr)
    expr.k = NatConst(2)
    expr = TupleAt(expr, NatConst(1))
    i += 1

