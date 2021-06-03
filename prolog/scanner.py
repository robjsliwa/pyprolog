from .token import Token
from .token_type import TokenType


def default_error_handler(line, message):
    print(f'Line[{line}] Error: {message}')
    raise Exception('Scanner error')


class Scanner:
    def __init__(self, source, report=default_error_handler):
        self._source = source
        self._tokens = []
        self._start = 0
        self._current = 0
        self._line = 1
        self._report = report

    def _add_token(self, token_type):
        self._add_token_with_literal(token_type, None)

    def _add_token_with_literal(self, token_type, literal):
        lexeme = self._source[self._start:self._current]
        self._tokens.append(
            Token(
                token_type,
                lexeme,
                literal,
                self._line
            )
        )

    def _is_at_end(self):
        return self._current >= len(self._source)

    def _advance(self):
        self._current += 1
        return self._source[self._current - 1]

    def _make_token(self, token_type, literal, line):
        lexeme = self._source[self._start:self._current]
        return Token(token_type, lexeme, literal, line)

    def _is_next(self, expected):
        if self._is_at_end():
            return False

        if self._source[self._current] != expected:
            return False

        self._current += 1
        return True

    def _peek(self):
        if self._is_at_end():
            return '\0'
        return self._source[self._current]

    def _peek_next(self):
        if self._current + 1 >= len(self._source):
            return '\0'
        return self._source[self._source + 1]

    def _is_digit(self, c):
        return c >= '0' and c <= '9'

    def _is_alphanumeric(self, c):
        return (c >= 'a' and c <= 'z') or \
            (c >= 'A' and c <= 'Z') or \
            (c >= '0' and c <= '9') or \
            (c == '_')

    def _is_lowercase_alpha(self, c):
        return c >= 'a' and c <= 'z'

    def _is_uppercase_alpha(self, c):
        return c >= 'A' and c <= 'Z'

    def _is_whitespace(self, c):
        return c == ' ' or c == '\r' or c == '\t' or c == '\n'

    def _process_atom(self):
        while self._is_alphanumeric(self._peek()):
            self._advance()

        self._add_token(TokenType.ATOM)

    def _process_variable(self):
        while self._is_alphanumeric(self._peek()):
            self._advance()

        self._add_token(TokenType.VARIABLE)

    def _scan_token(self):
        c = self._advance()

        if self._is_whitespace(c):
            pass
        elif self._is_lowercase_alpha(c):
            self._process_atom()
        elif self._is_uppercase_alpha(c) or c == '_':
            self._process_variable()
        elif c == '(':
            self._add_token(TokenType.LEFTPAREN)
        elif c == ')':
            self._add_token(TokenType.RIGHTPAREN)
        elif c == ':':
            if self._is_next('-'):
                self._add_token(TokenType.COLONMINUS)
            else:
                self._report(self._line, f'Expected `-` but found `{c}`')
        elif c == '.':
            self._add_token(TokenType.DOT)
        elif c == ',':
            self._add_token(TokenType.COMMA)
        else:
            self._report(self._line, f'Unexpected character: {c}')

    def tokenize(self):
        while self._is_at_end() is not True:
            self._start = self._current
            self._scan_token()

        self._add_token(TokenType.EOF)

        return self._tokens
