from lambdac import *
from replace import *

TRUE = Abstraction(Var('x'), Abstraction(Var('y'), Var('x')))
FALSE = Abstraction(Var('x'), Abstraction(Var('y'), Var('y')))
NOT = Abstraction(Var('x'), Application(Application(Var('x'), FALSE), TRUE))
OR = Abstraction(Var('x'), Abstraction(Var('y'), Application(Application(Var('x'), Var('x')), Var('y'))))
AND = Abstraction(Var('x'), Abstraction(Var('y'), Application(Application(Var('x'), Var('y')), Var('x'))))
IMPLIES = Abstraction(Var('x'), Abstraction(Var('y'), Application(Application(OR, Application(NOT, Var('x'))), Var('y'))))
EQUIV = Abstraction(Var('x'), Abstraction(Var('y'), Application(Application(AND, Application(Application(IMPLIES, Var('x')), Var('y'))), Application(Application(IMPLIES, Var('y')), Var('x')))))


ZERO = Abstraction(Var('f'), Abstraction(Var('x'), Var('x')))
SUCC = Abstraction(Var('n'), Abstraction(Var('f'), Abstraction(Var('x'), Application(Var('f'), Application(Application(Var('n'), Var('f')), Var('x'))))))
