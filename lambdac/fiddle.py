from lambdac import *
from replace import *

# TRUE = λx.λy.x
TRUE = Abstraction(
    Var('x'),
    Abstraction(
        Var('y'),
        Var('x')))

# FALSE = λx.λy.y
FALSE = Abstraction(
    Var('x'),
    Abstraction(
        Var('y'),
        Var('y')))


# NOT = λx.(x(λx.λy.y))(λx.λy.x)
#     = λx.(x FALSE) TRUE
NOT = Abstraction(
    Var('x'),
    Application(
        Application(
            Var('x'),
            FALSE),
        TRUE))

# OR = λx.λy.(xx)y
OR = Abstraction(
    Var('x'),
    Abstraction(
        Var('y'),
        Application(
            Application(
                Var('x'),
                Var('x')),
            Var('y'))))

# AND = λx.λy.(xy)x
AND = Abstraction(
    Var('x'),
    Abstraction(
        Var('y'),
        Application(
            Application(
                Var('x'),
                Var('y')),
            Var('x'))))

# IMPLIES = λx.λy.(OR (NOT x)) y
IMPLIES = Abstraction(
    Var('x'),
    Abstraction(
        Var('y'),
        Application(
            Application(
                OR,
                Application(
                    NOT,
                    Var('x'))),
                Var('y'))))


# EQUIV = λx.λy.AND (IMPLIES x y) (IMPLIES y x)
EQUIV = Abstraction(
    Var('x'),
    Abstraction(
        Var('y'),
        Application(
            Application(
                AND,
                Application(
                    Application(
                        IMPLIES,
                        Var('x')),
                    Var('y'))),
                Application(
                    Application(
                        IMPLIES,
                        Var('y')),
                    Var('x')))))

# ZERO = λf.λx.x
# (ZERO ≡ FALSE)
ZERO = Abstraction(
    Var('f'),
    Abstraction(
        Var('x'),
        Var('x')))

# give me a number n = λg.λx.gⁿ(x)
# and I will return λf.λx.f(fⁿ(x))
# SUCC = λn.λf.λx.f((nf)x)
SUCC = Abstraction(
    Var('n'),
    Abstraction(
        Var('f'),
        Abstraction(
            Var('x'),
            Application(
                Var('f'),
                Application(
                    Application(
                        Var('n'),
                        Var('f')),
                    Var('x'))))))

# number factory
def ntol(n):
    if n < 0:
        raise ValueError('Only positive numbers...')
    if n == 0:
        return ZERO
    return lambda_reduce(Application(SUCC, ntol(n - 1)))


def lton(expr):
    expr = lambda_reduce(expr)
    # assuming it is a number
    return str(lambda_reduce(expr)).count(expr.bind.name) - 1


# give me a number n = λg.λx.gⁿ(x)
# and a number     m = λh.λx.hᵐ(x)
# and I will return λf.λx.f⁽ⁿ⁺ᵐ⁾(x)
ADD = Abstraction(
        Var('n'),
        Abstraction(
            Var('m'),
            Application(
                Application(
                    Var('m'),
                    SUCC),
                Var('n'))))

# give me a number n = λg.λx.gⁿ(x)
# and a number     m = λh.λx.hᵐ(x)
# and I will return λf.λx.f⁽ⁿᵐ⁾(x)
# MUL = λn.λm.(λf.λx (n (mf)) x)
MUL = Abstraction(
        Var('n'),
        Abstraction(
            Var('m'),
            Abstraction(
                Var('f'),
                Abstraction(
                    Var('x'),
                    Application(
                        Application(
                            Var('n'),
                            Application(
                                Var('m'),
                                Var('f'))),
                        Var('x'))))))


# brain eplodes:
# MUL2 = λn.λm.(λf (n (mf)))
MUL2 = Abstraction(
        Var('n'),
        Abstraction(
            Var('m'),
            Abstraction(
                Var('f'),
                Application(
                    Var('n'),
                    Application(
                        Var('m'), Var('f'))))))
