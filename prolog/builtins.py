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

    def display(self):
        for arg in self.args:
            print(arg, end='')

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

    def display(self):
        print('')

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

    def display(self):
        print('', end='\t')

    def __str__(self):
        return 'nl'

    def __repr__(self):
        return str(self)
