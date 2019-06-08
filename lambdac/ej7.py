from lambdac import *
from extensions import *

f = Var('f')
first = BoolConst(True)
fun = Abstraction(f, Tuple(first, Application(f, f)))

second = Application(fun, fun)

expr = TupleAt(Tuple(first, second), NatConst(1))

i = 0
while i < 10:
    new_expr = expr.normal_eval()
    print(expr, 'evaluates to', new_expr)
    expr.k = NatConst(2)
    expr = TupleAt(expr, NatConst(1))
    i += 1
