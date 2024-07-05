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


class Dot:
    def __init__(self, head, tail=None):
        self._name = '.'
        self.head = head
        self.tail = tail
        self._current_element = self

    @classmethod
    def from_list(cls, lst):
        if not lst:
            return cls([])
        head = Dot(lst[0])
        first_head = head
        for elem in lst[1:]:
            head.tail = Dot(elem)
            head = head.tail
        return first_head

    @staticmethod
    def concat(dot1, dot2):
        return Dot.from_list(list(dot1) + list(dot2))

    def _match_lsts(self, lst1, lst2):
        m = list(map((lambda arg1, arg2: arg1.match(arg2)), lst1, lst2))

        return reduce(merge_bindings, [{}] + m)

    def match(self, other):
        if isinstance(other, Bar):
            return other.match(self)

        if not isinstance(other, Dot):
            return {}

        l1 = list(self)
        l2 = list(other)
        if len(l1) == len(l2):
            return self._match_lsts(l1, l2)
        return None

    def substitute(self, bindings):
        return Dot.from_list(
            list(map((lambda arg: arg.substitute(bindings)), self))
        )

    def query(self, runtime):
        yield from runtime.execute(self)

    def __iter__(self):
        self._current_element = self
        return self

    def __next__(self):
        if self._current_element is None:
            raise StopIteration
        element = self._current_element.head
        self._current_element = self._current_element.tail
        return element

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return str(self)


class Bar:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def match(self, other):
        if not isinstance(other, Dot):
            return None

        other_left = list(other)[: len(list(self.head))]
        other_right = list(other)[len(list(self.head)) :]
        other_head = Dot.from_list(other_left)
        other_tail = Dot.from_list(other_right)
        head_match = self.head.match(other_head)
        tail_match = self.tail.match(other_tail)

        if head_match is not None and tail_match is not None:
            return {**head_match, **tail_match}

        return None

    def substitute(self, bindings):
        # return Dot.from_list(list(map(
        #     (lambda arg: arg.substitute(bindings)),
        #     self
        # )))
        new_head = self.head.substitute(bindings)
        new_tail = self.tail.substitute(bindings)
        return Bar(new_head, new_tail)

    def query(self, runtime):
        yield from runtime.execute(self)

    def __str__(self):
        output = '['
        output += ', '.join(map(str, self.head))
        if self.tail:
            output += f' | {self.tail}'
        output += ']'
        return output

    def __repr__(self):
        return str(self)


class Term:
    def __init__(self, pred, *args):
        self.pred = pred
        self.args = list(args)

    def match(self, other):
        if isinstance(other, Term):
            if self.pred != other.pred or len(self.args) != len(other.args):
                return None

            m = list(
                map(
                    (lambda arg1, arg2: arg1.match(arg2)), self.args, other.args
                )
            )

            return reduce(merge_bindings, [{}] + m)

        return other.match(self)

    def substitute(self, bindings):
        return Term(
            self.pred, *map((lambda arg: arg.substitute(bindings)), self.args)
        )

    def query(self, runtime):
        yield from runtime.execute(self)

    def __str__(self):
        if len(self.args) == 0:
            return f'{self.pred}'
        args = ', '.join(map(str, self.args))
        return f'{self.pred}({args})'

    def __repr__(self):
        return str(self)


class TermFunction(Term):
    def __init__(self, func, predicate, *args):
        super().__init__(predicate, *args)
        self._func = func

    def _execute_func(self):
        result = next(self._func())
        if isinstance(result, tuple):
            self.args = [*result]
        else:
            self.args = [result]

    def match(self, other):
        if isinstance(other, Term):
            if self.pred != other.pred or len(self.args) != len(other.args):
                return None

            self._execute_func()
            m = list(
                map(
                    (lambda arg1, arg2: arg1.match(arg2)), self.args, other.args
                )
            )

            return reduce(merge_bindings, [{}] + m)

        return other.match(self)


class Logic:
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


class CUT(Term):
    def __init__(self):
        super().__init__(CUT)

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
