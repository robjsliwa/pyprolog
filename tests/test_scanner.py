from prolog.scanner import Scanner
from prolog.token import Token
from prolog.token_type import TokenType


def test_scanner():
    source = '''
    has(tom, cat)
        has(bob, cat).

    has(peter, dog)

    owns(Owner, Pet) :- has(Owner, Pet).
    '''

    tokens = Scanner(source).tokenize()

    expected_tokens = [
        Token(TokenType.ATOM, 'has', None, 0),
        Token(TokenType.LEFTPAREN, '(', None, 0),
        Token(TokenType.ATOM, 'tom', None, 0),
        Token(TokenType.COMMA, ',', None, 0),
        Token(TokenType.ATOM, 'cat', None, 0),
        Token(TokenType.RIGHTPAREN, ')', None, 0),
        Token(TokenType.ATOM, 'has', None, 0),
        Token(TokenType.LEFTPAREN, '(', None, 0),
        Token(TokenType.ATOM, 'bob', None, 0),
        Token(TokenType.COMMA, ',', None, 0),
        Token(TokenType.ATOM, 'cat', None, 0),
        Token(TokenType.RIGHTPAREN, ')', None, 0),
        Token(TokenType.DOT, '.', None, 0),
        Token(TokenType.ATOM, 'has', None, 0),
        Token(TokenType.LEFTPAREN, '(', None, 0),
        Token(TokenType.ATOM, 'peter', None, 0),
        Token(TokenType.COMMA, ',', None, 0),
        Token(TokenType.ATOM, 'dog', None, 0),
        Token(TokenType.RIGHTPAREN, ')', None, 0),
        Token(TokenType.ATOM, 'owns', None, 0),
        Token(TokenType.LEFTPAREN, '(', None, 0),
        Token(TokenType.VARIABLE, 'Owner', None, 0),
        Token(TokenType.COMMA, ',', None, 0),
        Token(TokenType.VARIABLE, 'Pet', None, 0),
        Token(TokenType.RIGHTPAREN, ')', None, 0),
        Token(TokenType.COLONMINUS, ':-', None, 0),
        Token(TokenType.ATOM, 'has', None, 0),
        Token(TokenType.LEFTPAREN, '(', None, 0),
        Token(TokenType.VARIABLE, 'Owner', None, 0),
        Token(TokenType.COMMA, ',', None, 0),
        Token(TokenType.VARIABLE, 'Pet', None, 0),
        Token(TokenType.RIGHTPAREN, ')', None, 0),
        Token(TokenType.DOT, '.', None, 0),
        Token(TokenType.EOF, ' ', None, 0)
    ]

    for index, token in enumerate(tokens):
        assert token.token_type == expected_tokens[index].token_type
        assert token.lexeme == expected_tokens[index].lexeme
