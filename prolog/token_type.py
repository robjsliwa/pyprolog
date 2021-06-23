from enum import Enum, auto


class TokenType(Enum):
    ATOM = auto(),
    VARIABLE = auto(),
    NUMBER = auto(),
    LEFTPAREN = auto(),
    RIGHTPAREN = auto(),
    COLONMINUS = auto(),
    COMMA = auto(),
    DOT = auto(),
    UNDERSCORE = auto(),
    SINGLEQUOTE = auto(),
    FAIL = auto(),
    WRITE = auto(),
    NL = auto(),
    TAB = auto(),
    EOF = auto()
