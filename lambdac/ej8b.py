from lambdac import *
from extensions import *


e = BoolConst(True)

# letrec f ≡ λx.if e then True else (f)(x) in ((f)(0) + 1)
exp = Letrec(
    Var('f'),
    Abstraction(
        Var('x'),
        If(
            e,
            BoolConst(True),
            Application(
                Var('f'),
                Var('x')))),
    Plus(
        Application(
            Var('f'),
            NatConst(0)),
        NatConst(1)))

exp.eager_eval(verbose=True)
