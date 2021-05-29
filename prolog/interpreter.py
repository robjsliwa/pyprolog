from functools import reduce


def merge_bindings(bindings1, bindings2):
    if bindings1 is None or bindings2 is None:
        return None

    bindings = dict()

    bindings = {**bindings1}

    for variable, value in bindings2.items():
        if variable in bindings:
            other = bindings[variable]
            sub = other.match(value)

            if sub is not None:
                for var, val in sub.items():
                    bindings[var] = val
            else:
                return None
        else:
            bindings[variable] = value

    return bindings


class Variable:
    def __init__(self, name):
        self.name = name

    def match(self, other):
        bindings = dict()
        if self != other:
            bindings[self] = other
        return bindings

    def substitute(self, bindings):
        value = bindings.get(self, None)
        if value is not None:
            return value.substitute(bindings)
        return self

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)


class Term:
    def __init__(self, pred, *args):
        self.pred = pred
        self.args = list(args)

    def match(self, other):
        if isinstance(other, Term):
            if self.pred != other.pred or \
               len(self.args) != len(other.args):
                return None

            m = list(
                    map(
                        (lambda arg1, arg2: arg1.match(arg2)),
                        self.args,
                        other.args
                    )
            )

            return reduce(merge_bindings, [{}] + m)

        return other.match(self)

    def substitute(self, bindings):
        return Term(self.pred, *map(
            (lambda arg: arg.substitute(bindings)),
            self.args
        ))

    def query(self, runtime):
        yield from runtime.execute(self)

    def __str__(self):
        if len(self.args) == 0:
            return f'{self.pred}'
        args = ', '.join(map(str, self.args))
        return f'{self.pred}({args})'

    def __repr__(self):
        return str(self)


class TRUE(Term):
    def __init__(self):
        super().__init__(TRUE)

    def substitute(self, bindings):
        return self

    def query(self, runtime):
        yield self


class Rule:
    def __init__(self, head, body):
        self.head = head
        self.body = body


class Conjunction(Term):
    def __init__(self, args):
        super().__init__(None, *args)

    def query(self, runtime):
        def solutions(index, bindings):
            if index >= len(self.args):
                yield self.substitute(bindings)
            else:
                arg = self.args[index]
                for item in runtime.execute(arg.substitute(bindings)):
                    unified = merge_bindings(
                        arg.match(item),
                        bindings
                    )
                    if unified is not None:
                        yield from solutions(index + 1, unified)

        yield from solutions(0, {})

    def substitute(self, bindings):
        return Conjunction(
            map(
                (lambda arg: arg.substitute(bindings)),
                self.args
            )
        )


class Runtime:
    def __init__(self, rules):
        self.rules = rules

    def execute(self, goal):
        for rule in self.rules:
            match = rule.head.match(goal)
            if match is not None:
                head = rule.head.substitute(match)
                body = rule.body.substitute(match)
                for item in body.query(self):
                    yield head.substitute(body.match(item))
