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


class List:
    def __init__(self, lst, tail=None):
        self.name = 'list'
        self.lst = lst
        self.tail = tail

    def _match_lsts(self, lst1, lst2):
        m = list(
                map(
                    (lambda arg1, arg2: arg1.match(arg2)),
                    lst1,
                    lst2
                )
        )

        return reduce(merge_bindings, [{}] + m)

    def match(self, other):
        '''
        list                 tail
        ---------------------------------------
        list                None
        list                Variable
        list                List
        Variable            None
        Variable            Variable
        Variable            List
        '''
        if not isinstance(other, List):
            return {}

        if isinstance(self.lst, list) and \
           len(other.lst) >= len(self.lst):
            if isinstance(self.tail, Variable):
                left_lst = other.lst[:len(self.lst)]
                right_lst = other.lst[len(self.lst):]
                bindings = self._match_lsts(self.lst, left_lst)
                bindings[self.tail] = List(right_lst)
                return bindings
            elif isinstance(self.tail, List):
                left_lst = other.lst[:1]
                right_lst = other.lst[1:]
                bindings_lst = self._match_lsts(self.lst, left_lst)
                bindings_tail = self._match_lsts(self.tail.lst, right_lst)
                return merge_bindings(bindings_lst, bindings_tail)
            elif self.tail is None and len(self.lst) == len(other.lst):
                return self._match_lsts(self.lst, other.lst)
        elif isinstance(self.lst, Variable):
            if len(other.lst) == 0:
                return {}
            if isinstance(self.tail, Variable):
                left_lst = other.lst[:1]
                right_lst = other.lst[1:]
                bindings = {
                    self.lst: left_lst[0],
                    self.tail: List(right_lst)
                }
                return bindings
            elif isinstance(self.tail, List):
                left_lst = other.lst[:1]
                right_lst = other.lst[1:]
                bindings_lst = {
                    self.lst: left_lst[0]
                }
                bindings_tail = self._match_lsts(self.tail.lst, right_lst)
                return merge_bindings(bindings_lst, bindings_tail)

        return {}

    def substitute(self, bindings):
        main_lst = None

        if isinstance(self.lst, Variable):
            main_lst = self.lst.substitute(bindings)
        else:
            main_lst = list(map(
                (lambda arg: arg.substitute(bindings)),
                self.lst
            ))

        lst_sub = List(main_lst)

        if self.tail:
            lst_sub = List(
                main_lst,
                self.tail.substitute(bindings)
            )

        return lst_sub

    def query(self, runtime):
        yield from runtime.execute(self)

    def __str__(self):
        left_part = ", ".join(map(str, self.lst)) \
            if isinstance(self.lst, list) else self.lst
        if self.tail:
            return f'[{left_part} | {self.tail}]'

        return f'[{left_part}]'

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
