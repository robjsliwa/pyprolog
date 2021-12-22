from abc import ABC, abstractmethod
from .merge_bindings import merge_bindings


class Fail:
    def __init__(self):
        self.name = 'fail'

    def match(self, other):
        return None

    def substitute(self, bindings):
        return self

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)


class Write:
    def __init__(self, *args):
        self.pred = 'write'
        self.args = list(args)

    def match(self, other):
        return {}

    def substitute(self, bindings):
        result = Write(*map(
            (lambda arg: arg.substitute(bindings)),
            self.args
        ))
        return result

    def display(self, stream_writer):
        for arg in self.args:
            stream_writer(str(arg))

    def __str__(self):
        if len(self.args) == 0:
            return f'{self.pred}'
        args = ', '.join(map(str, self.args))
        return f'{self.pred}({args})'

    def __repr__(self):
        return str(self)


class Nl:
    def __init__(self):
        self.pred = 'nl'

    def match(self, other):
        return {}

    def substitute(self, bindings):
        return Nl()

    def display(self, stream_writer):
        stream_writer('\n')

    def __str__(self):
        return 'nl'

    def __repr__(self):
        return str(self)


class Tab:
    def __init__(self):
        self.pred = 'tab'

    def match(self, other):
        return {}

    def substitute(self, bindings):
        return Tab()

    def display(self, stream_writer):
        stream_writer('\t')

    def __str__(self):
        return self.pred

    def __repr__(self):
        return str(self)


class DatabaseOp(ABC):
    def match(self, other):
        bindings = dict()
        if self != other:
            bindings[self] = other
        return bindings

    @abstractmethod
    def substitute(self, bindings):
        pass

    @abstractmethod
    def execute(self, remove_rule):
        pass

    def query(self, runtime, bindings={}):
        param_bound = list(self.arg.query(runtime))
        if param_bound:
            param_bound = param_bound[0]
            unified = merge_bindings(
                self.match(param_bound),
                bindings
            )
            self.substitute(unified).execute(runtime)
        else:
            self.execute(runtime)
        yield bindings


class Retract(DatabaseOp):
    def __init__(self, arg):
        self.pred = 'retract'
        self.arg = arg

    def substitute(self, bindings):
        value = bindings.get(self, None)
        if value is not None:
            return Retract(value.substitute(bindings))
        return Retract(self.arg.substitute(bindings))

    def execute(self, runtime):
        runtime.remove_rule(self.arg)

    def __str__(self):
        return f'{self.pred}({self.arg})'

    def __repr__(self):
        return str(self)


class AssertA(DatabaseOp):
    def __init__(self, arg):
        self.pred = 'asserta'
        self.arg = arg

    def substitute(self, bindings):
        value = bindings.get(self, None)
        if value is not None:
            return AssertA(value.substitute(bindings))
        return AssertA(self.arg.substitute(bindings))

    def execute(self, runtime):
        runtime.insert_rule_left(self.arg)

    def __str__(self):
        return f'{self.pred}({self.arg})'

    def __repr__(self):
        return str(self)


class AssertZ(DatabaseOp):
    def __init__(self, arg):
        self.pred = 'assertz'
        self.arg = arg

    def substitute(self, bindings):
        value = bindings.get(self, None)
        if value is not None:
            return AssertZ(value.substitute(bindings))
        return AssertZ(self.arg.substitute(bindings))

    def execute(self, runtime):
        runtime.insert_rule_right(self.arg)

    def __str__(self):
        return f'{self.pred}({self.arg})'

    def __repr__(self):
        return str(self)
