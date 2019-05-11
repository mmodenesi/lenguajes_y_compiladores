from comm import *
from intexp import *
from boolexp import *
from utils import concat
from state import State
from replace import Delta


program = concat([
    Assign(Var('x'), Const(10)),
    While(
        Geq(Var('x'), Const(0)),
        Concat(
            Assign(Var('x'), Plus(Var('x'), Const(-1))),
            NewVar(Var('x'), Const(200), Assign(Var('x2'), Plus(Var('x'), Const(2))))))
    ])

print('Programa:')
print(program)
result = program.sem(State())
print(result)

delta = Delta()
delta[Var('x')] = Var('x7')
delta[Var('x2')] = Var('x5')


print('Programa aplicando el reemplazo', delta)
newprogram = program.replace(delta)
print(newprogram)
result = newprogram.sem(State())
print(result)
