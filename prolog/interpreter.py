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


class Arithmetic:
    def __init__(self, var, expression):
        self._var = var
        self._expression = expression

    @property
    def args(self):
        return [self._var]

    @property
    def var(self):
        return self._var

    def match(self, other):
        return {}

    def evaluate(self):
        exp_val = self._expression.evaluate()
        return exp_val

    def substitute(self, bindings):
        return self

    def __str__(self):
        return f'{self._var}'

    def __repr__(self):
        return str(self)


class BinaryExpression:
    def __init__(self, left, operator, right):
        self._left = left
        self._operator = operator
        self._right = right


class UnaryExpression:
    def __init__(self, operator, right):
        self._operator = operator
        self._right = right


class PrimaryExpression:
    def __init__(self, exp):
        self._exp = exp

    def evaluate(self):
        return self._exp


class Number(Term):
    def __init__(self, pred):
        super().__init__(pred)


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

    def __str__(self):
        return f'{self.head}{self.body}'

    def __repr__(self):
        return str(self)


class Conjunction(Term):
    def __init__(self, args):
        super().__init__(None, *args)

    def _is_builtin(self, arg):
        if isinstance(arg, Write) or \
           isinstance(arg, Nl) or \
           isinstance(arg, Tab):
            return True
        return False

    def query(self, runtime):
        def solutions(index, bindings):
            if index >= len(self.args):
                yield self.substitute(bindings)
            else:
                arg = self.args[index]
                if self._is_builtin(arg):
                    arg.substitute(bindings).display()
                    yield from solutions(index + 1, bindings)
                elif isinstance(arg, Arithmetic):
                    val = arg.substitute(bindings).evaluate()
                    unified = merge_bindings(
                        {arg._var: val},
                        bindings
                    )
                    yield from solutions(index + 1, unified)
                else:
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


class Runtime:
    def __init__(self, rules):
        self.rules = rules

    def all_rules(self, query):
        if isinstance(query, Rule):
            return self.rules + [query]
        return self.rules

    def execute(self, query):
        goal = query
        if isinstance(query, Rule):
            goal = query.head
        for rule in self.all_rules(query):
            match = rule.head.match(goal)
            if match is not None:
                head = rule.head.substitute(match)
                body = rule.body.substitute(match)
                for item in body.query(self):
                    yield head.substitute(body.match(item))
