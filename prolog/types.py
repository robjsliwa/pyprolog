from functools import reduce
from .math_interpreter import MathInterpreter
from .logic_interpreter import LogicInterpreter
from .expression import Visitor, PrimaryExpression, BinaryExpression
from .merge_bindings import merge_bindings


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


class Logic():
    def __init__(self, expression):
        self._expression = expression

    def match(self, other):
        bindings = dict()
        if self != other:
            bindings[self] = self.evaluate()
        return bindings

    def substitute(self, bindings):
        value = bindings.get(self, None)
        if value is not None:
            return value.substitute(bindings)

        expression_binder = ExpressionBinder(bindings)
        expression = self._expression.accept(expression_binder)
        return Logic(expression)

    def evaluate(self):
        return self._expression.accept(logic_interpreter)

    def query(self, runtime):
        yield self.evaluate()

    def __str__(self):
        return f'{self._expression}'

    def __repr__(self):
        return str(self)


class Arithmetic(Variable):
    def __init__(self, name, expression):
        super().__init__(name)
        self._expression = expression

    @property
    def args(self):
        return [self]

    @property
    def var(self):
        return self

    def _bind_name(self, bindings):
        for k, v in bindings.items():
            if isinstance(k, Variable) and k.name == self.name:
                if isinstance(v, Variable):
                    return v.name
        return self.name

    def match(self, other):
        bindings = dict()
        if self != other:
            bindings[self] = self.evaluate()
        return bindings

    def substitute(self, bindings):
        value = bindings.get(self, None)
        if value is not None:
            return value.substitute(bindings)

        expression_binder = ExpressionBinder(bindings)
        name = self._bind_name(bindings)
        expression = self._expression.accept(expression_binder)
        return Arithmetic(name, expression)

    def evaluate(self):
        val = self._expression.accept(math_interpreter)
        return val

    def query(self, runtime):
        yield self

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return str(self)


class Number(Term):
    def __init__(self, pred):
        super().__init__(pred)

    def multiply(self, number):
        return Number(self.pred * number.pred)

    def divide(self, number):
        return Number(self.pred / number.pred)

    def add(self, number):
        return Number(self.pred + number.pred)

    def substract(self, number):
        return Number(self.pred - number.pred)

    def equal(self, number):
        if self.pred == number.pred:
            return TRUE()
        return FALSE()

    def not_equal(self, number):
        if self.pred != number.pred:
            return TRUE()
        return FALSE()

    def equal_less(self, number):
        if self.pred <= number.pred:
            return TRUE()
        return FALSE()

    def less(self, number):
        if self.pred < number.pred:
            return TRUE()
        return FALSE()

    def greater_equal(self, number):
        if self.pred >= number.pred:
            return TRUE()
        return FALSE()

    def greater(self, number):
        if self.pred > number.pred:
            return TRUE()
        return FALSE()


class TRUE(Term):
    def __init__(self):
        super().__init__(TRUE)

    def substitute(self, bindings):
        return self

    def query(self, runtime):
        yield self


class FALSE(Term):
    def __init__(self):
        super().__init__(FALSE)

    def substitute(self, bindings):
        return {}

    def query(self, runtime):
        yield self


class ExpressionBinder(Visitor):
    """Binds variables.

    This class given dictionary of variable bindings walks expression tree
    and substitutes each variable for the value found in bindings dictionary.
    This returns identical expression tree as the input but with variables
    replaced with values.
    """
    def __init__(self, bindings):
        self._bindings = bindings

    def _bind_expr(self, expr):
        return expr.accept(self)

    def visit_binary(self, expr):
        left = self._bind_expr(expr.left)
        right = self._bind_expr(expr.right)

        return BinaryExpression(left, expr.operand, right)

    def visit_primary(self, expr):
        exp = expr.exp
        if isinstance(exp, Variable):
            for k, v in self._bindings.items():
                if k.name == exp.name:
                    return PrimaryExpression(v)

        return expr


math_interpreter = MathInterpreter()
logic_interpreter = LogicInterpreter()
