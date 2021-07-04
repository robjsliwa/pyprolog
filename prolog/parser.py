from prolog.token_type import TokenType
from .interpreter import Arithmetic, Conjunction, PrimaryExpression, \
    Variable, Term, Rule, TRUE, Number, Fail, Write, Nl, Tab


def default_error_handler(line, message):
    print(f'Line[{line}] Error: {message}')
    raise Exception('Parser error')


class Parser:
    def __init__(self, tokens, report=default_error_handler):
        self._current = 0
        self._is_done = False
        self._scope = {}
        self._tokens = tokens
        self._report = report

    def _peek(self):
        return self._tokens[self._current]

    def _peek_next(self):
        return self._tokens[self._current + 1]

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
        if isinstance(token_type, list):
            return self._peek().token_type in token_type
        return self._peek().token_type == token_type

    def _is_type(self, token, token_type):
        return token.token_type == token_type

    def _create_variable(self, predicate):
        variable = self._scope.get(predicate, None)
        if variable is None:
            variable = Variable(predicate)
            self._scope[predicate] = variable
        return variable

    def _parse_primary_expression(self):
        token = self._peek()

        if self._is_type(token, TokenType.NUMBER):
            self._advance()
            number_value = token.literal
            return PrimaryExpression(Number(number_value))
        elif self._is_type(token, TokenType.VARIABLE):
            self._advance()
            return PrimaryExpression(
                self._create_variable(token.lexeme)
            )

        self._report(
            self._peek().line,
            f'Expected number or variable but got: {token}'
        )

    def _parse_expression(self, token):
        var = self._create_variable(token.lexeme)
        self._advance()  # consume IS

        expr = self._parse_primary_expression()
        return Arithmetic(var, expr)

    def _parse_atom(self):
        token = self._peek()
        if not self._token_matches([
            TokenType.VARIABLE,
            TokenType.UNDERSCORE,
            TokenType.NUMBER,
            TokenType.FAIL,
            TokenType.WRITE,
            TokenType.NL,
            TokenType.TAB,
            TokenType.ATOM
        ]):
            self._report(token.line, f'Bad atom name: {token.lexeme}')

        if self._is_type(token, TokenType.NUMBER):
            if self._peek_next().token_type == TokenType.COLONMINUS or \
               self._peek_next().token_type == TokenType.DOT or \
               self._peek_next().token_type == TokenType.LEFTPAREN:
                self._report(
                    self._peek().line,
                    f'Number cannot be a rule: {self._peek()}'
                )

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
                    self._report(
                        self._peek().line,
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

            if self._is_type(token, TokenType.VARIABLE) and \
               self._peek().token_type == TokenType.IS:
                return self._parse_expression(token)

            return self._create_variable(predicate)

        if self._is_type(token, TokenType.FAIL):
            return Fail()

        if self._is_type(token, TokenType.NL):
            return Nl()

        if self._is_type(token, TokenType.TAB):
            return Tab()

        if self._is_type(token, TokenType.NUMBER):
            number_value = token.literal
            return Number(number_value)

        if not self._token_matches(TokenType.LEFTPAREN):
            return Term(predicate)

        self._advance()
        args = []
        while not self._token_matches(TokenType.RIGHTPAREN):
            args.append(self._parse_term())
            if not self._token_matches(TokenType.COMMA) and \
               not self._token_matches(TokenType.RIGHTPAREN):
                self._report(
                    self._peek().line,
                    f'Expected , or ) in term but got {self._peek()}')

            if self._token_matches(TokenType.COMMA):
                self._advance()

        self._advance()

        if self._is_type(token, TokenType.WRITE):
            return Write(*args)

        return Term(predicate, *args)

    def _parse_rule(self):
        head = self._parse_term()

        if self._token_matches(TokenType.DOT):
            self._advance()
            return Rule(head, TRUE())

        if not self._token_matches(TokenType.COLONMINUS):
            self._report(
                self._peek().line,
                f'Expected :- in rule but got {self._peek()}')

        self._advance()
        args = []
        while not self._token_matches(TokenType.DOT):
            args.append(self._parse_term())
            if not self._token_matches(TokenType.COMMA) and \
               not self._token_matches(TokenType.DOT):
                self._report(
                    self._peek().line,
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

    def _all_vars(self, terms):
        variables = []
        for term in terms:
            if isinstance(term, Term):
                for arg in term.args:
                    if isinstance(arg, Variable):
                        if arg not in variables:
                            variables.append(arg)
        return variables

    def _parse_query(self):
        head = self._parse_term()

        if self._token_matches(TokenType.DOT):
            self._advance()
            return head

        if self._token_matches(TokenType.COLONMINUS):
            self._report(
                self._peek().line,
                'Cannot use rule as a query')

        self._advance()
        args = [head]
        while not self._token_matches(TokenType.DOT):
            args.append(self._parse_term())
            if not self._token_matches(TokenType.COMMA) and \
               not self._token_matches(TokenType.DOT):
                self._report(
                    self._peek().line,
                    f'Expected , or . in term but got {self._peek()}')

            if self._token_matches(TokenType.COMMA):
                self._advance()

        self._advance()

        head = Term('##')
        vars = self._all_vars(args)
        if len(vars) > 0:
            head = Term('##', *vars)

        return Rule(head, Conjunction(args))

    def parse_rules(self):
        rules = []
        while not self._is_done:
            self._scope = {}
            rules.append(self._parse_rule())
        return rules

    def parse_terms(self):
        self._scope = {}
        return self._parse_term()

    def parse_query(self):
        self._scope = {}
        return self._parse_query()
