import re
from .interpreter import Conjunction, Variable, Term, Rule, TRUE


TOKEN_REGEX = r"[A-Za-z0-9_]+|:\-|[()\.,]"
ATOM_NAME_REGEX = r"^[A-Za-z0-9_]+$"
VARIABLE_REGEX = r"^[A-Z_][A-Za-z0-9_]*$"


def lexer(text):
    matches = re.findall(TOKEN_REGEX, text)

    for token in matches:
        yield token


class Parser:
    def __init__(self, tokens):
        self._current = ''
        self._is_done = False
        self._scope = {}
        self._tokens = tokens
        self._advance()

    def _advance(self):
        try:
            next_token = next(self._tokens)
            self._current = next_token
        except StopIteration:
            self._is_done = True

    def _parse_atom(self):
        name = self._current
        if re.match(ATOM_NAME_REGEX, name) is None:
            raise Exception(f'Bad atom name: {name}')

        self._advance()
        return name

    def _parse_term(self):
        if self._current == '(':
            self._advance()
            args = []
            while self._current != ')':
                args.append(self._parse_term())
                if self._current != ',' and self._current != ')':
                    raise Exception(
                        f'Expecter , or ) in term but got {self._current}')
                if self._current == ',':
                    self._advance()

            self._advance()
            return Conjunction(args)

        predicate = self._parse_atom()
        if re.match(VARIABLE_REGEX, predicate) is not None:
            if predicate == '_':
                return Variable('_')

            variable = self._scope.get(predicate, None)
            if variable is None:
                variable = Variable(predicate)
                self._scope[predicate] = variable
            return variable

        if self._current != '(':
            return Term(predicate)

        self._advance()
        args = []
        while self._current != ')':
            args.append(self._parse_term())
            if self._current != ',' and self._current != ')':
                raise Exception(
                    f'Expected , or ) in term but got {self._current}')

            if self._current == ',':
                self._advance()

        self._advance()
        return Term(predicate, *args)

    def _parse_rule(self):
        head = self._parse_term()

        if self._current == '.':
            self._advance()
            return Rule(head, TRUE())

        if self._current != ':-':
            raise Exception(f'Expected :- in rule but got {self._current}')

        self._advance()
        args = []
        while self._current != '.':
            args.append(self._parse_term())
            if self._current != ',' and self._current != '.':
                raise Exception(
                    f'Expected , or ) in term but got {self._current}')

            if self._current == ',':
                self._advance()

        self._advance()
        body = None
        if len(args) == 1:
            body = args[0]
        else:
            body = Conjunction(args)

        return Rule(head, body)

    def parse_rules(self):
        rules = []
        while not self._is_done:
            self._scope = {}
            rules.append(self._parse_rule())
        return rules

    def parse_terms(self):
        self._scope = {}
        return self._parse_term()
