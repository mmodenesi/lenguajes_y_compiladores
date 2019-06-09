from lambdac import *
from extensions import *


e = BoolConst(True)

# letrec f ≡ λx.if e then 1 else f x in f 0
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

exp.normal_eval(verbose=True)
