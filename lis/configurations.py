from comm import *
from state import State


class Configuration:
    def __init__(self, command, state):
        self.command = command
        self.state = state

    def is_terminal(self):
        return self.command is None

    def make_one_step(self):
        if isinstance(self.command, (Skip, Assign)):
            return Configuration(command=None, state=self.command.sem(self.state))
        if isinstance(self.command, Concat):
            next_config = Configuration(self.command.c0, self.state.copy()).make_one_step()
            if next_config.is_terminal():
                return Configuration(self.command.c1, next_config.state)
            else:
                return Configuration(
                    Concat(next_config.command, self.command.c1), next_config.state)
        if isinstance(self.command, If):
            if self.command.b.sem(self.state):
                return Configuration(self.command.c0, self.state)
            else:
                return Configuration(self.command.c1, self.state)
        if isinstance(self.command, While):
            if self.command.b.sem(self.state):
                return Configuration(Concat(self.command.c, self.command), self.state)
            else:
                return Configuration(None, self.state)
        if isinstance(self.command, NewVar):
            scoped = Assign(self.command.var, self.command.intexp).sem(self.state.copy())
            next_config = Configuration(self.command.c, scoped).make_one_step()
            if next_config.is_terminal():
                next_config.state[self.command.var] = self.state[self.command.var]
                return next_config
            else:
                command = NewVar(self.command.var,
                                 Const(next_config.state[self.command.var]),
                                 next_config.command)
                next_config.state[self.command.var] = self.state[self.command.var]
                return Configuration(command, next_config.state)





    def __str__(self):
        if self.is_terminal():
            return str(self.state)
        else:
            return '<{}, {}>'.format(self.command, self.state)


class Execution:
    def __init__(self, configuration):
        self.configuration = configuration

    def step(self):
        if not self.configuration.is_terminal():
            self.configuration = self.configuration.make_one_step()
        else:
            raise ValueError('Execution ended')


def execute(program, state=None):
    state = state or State()
    execution = Execution(Configuration(program, state))

    while True:
        print(execution.configuration)
        try:
            execution.step()
        except ValueError:
            print('Execution done')
            break
