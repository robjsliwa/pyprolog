from prolog.token_type import TokenType
from .interpreter import Conjunction, Variable, Term, Rule, TRUE


class Parser:
    def __init__(self, tokens):
        self._current = 0
        self._is_done = False
        self._scope = {}
        self._tokens = tokens

    def _peek(self):
        return self._tokens[self._current]

    def _is_at_end(self):
        return self._peek().token_type == TokenType.EOF

    def _previous(self):
        return self._tokens[self._current - 1]

    def _advance(self):
        self._current += 1
        if self._is_at_end():
            self._is_done = True
        return self._previous()

    def _token_matches(self, token_type):
        return self._peek().token_type == token_type

    def _is_type(self, token, token_type):
        return token.token_type == token_type

    def _parse_atom(self):
        token = self._peek()
        if not self._token_matches(TokenType.VARIABLE) and \
           not self._token_matches(TokenType.UNDERSCORE) and \
           not self._token_matches(TokenType.ATOM):
            raise Exception(f'Bad atom name: {token.lexeme}')

        self._advance()
        return token

    def _parse_term(self):
        if self._token_matches(TokenType.LEFTPAREN):
            self._advance()
            args = []
            while not self._token_matches(TokenType.RIGHTPAREN):
                args.append(self._parse_term())
                if not self._token_matches(TokenType.COMMA) and \
                   not self._token_matches(TokenType.RIGHTPAREN):
                    raise Exception(
                        f'Expecter , or ) in term but got {self._peek()}')
                if self._token_matches(TokenType.COMMA):
                    self._advance()

            self._advance()
            return Conjunction(args)

        token = self._parse_atom()
        predicate = token.lexeme
        if self._is_type(token, TokenType.VARIABLE) or \
           self._is_type(token, TokenType.UNDERSCORE):
            if self._is_type(token, TokenType.UNDERSCORE):
                return Variable('_')

            variable = self._scope.get(predicate, None)
            if variable is None:
                variable = Variable(predicate)
                self._scope[predicate] = variable
            return variable

        if not self._token_matches(TokenType.LEFTPAREN):
            return Term(predicate)

        self._advance()
        args = []
        while not self._token_matches(TokenType.RIGHTPAREN):
            args.append(self._parse_term())
            if not self._token_matches(TokenType.COMMA) and \
               not self._token_matches(TokenType.RIGHTPAREN):
                raise Exception(
                    f'Expected , or ) in term but got {self._peek()}')

            if self._token_matches(TokenType.COMMA):
                self._advance()

        self._advance()
        return Term(predicate, *args)

    def _parse_rule(self):
        head = self._parse_term()

        if self._token_matches(TokenType.DOT):
            self._advance()
            return Rule(head, TRUE())

        if not self._token_matches(TokenType.COLONMINUS):
            raise Exception(f'Expected :- in rule but got {self._peek()}')

        self._advance()
        args = []
        while not self._token_matches(TokenType.DOT):
            args.append(self._parse_term())
            if not self._token_matches(TokenType.COMMA) and \
               not self._token_matches(TokenType.DOT):
                raise Exception(
                    f'Expected , or . in term but got {self._peek()}')

            if self._token_matches(TokenType.COMMA):
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
