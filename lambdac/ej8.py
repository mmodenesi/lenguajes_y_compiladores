from lambdac import *
from extensions import *


e = BoolConst(False)

exp = Letrec(
    Var('f'),
    Abstraction(
        Var('x'),
        If(
            e,
            NatConst(1),
            Application(
                Var('f'),
                Var('x')))),
    Application(
        Var('f'),
        NatConst(0)))

eager_evaluation(exp, verbose=True)
