from abc import ABC, abstractmethod


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass


class Visitor(ABC):
    @abstractmethod
    def visit_binary(self, expr):
        pass

    @abstractmethod
    def visit_primary(self, expr):
        pass


class BinaryExpression(Expr):
    def __init__(self, left, operand, right):
        self.left = left
        self.operand = operand
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary(self)

    def __str__(self):
        return f'{self.left} {self.operand} {self.right}'

    def __repr__(self):
        return str(self)


class UnaryExpression:
    def __init__(self, operand, right):
        self.operand = operand
        self.right = right


class PrimaryExpression:
    def __init__(self, exp):
        self.exp = exp

    def accept(self, visitor):
        return visitor.visit_primary(self)

    def __str__(self):
        return f'{self.exp}'

    def __repr__(self):
        return str(self)
