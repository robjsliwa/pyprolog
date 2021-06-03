from enum import Enum, auto


class TokenType(Enum):
    ATOM = auto(),
    VARIABLE = auto(),
    LEFTPAREN = auto(),
    RIGHTPAREN = auto(),
    COLONMINUS = auto(),
    COMMA = auto(),
    DOT = auto(),
    UNDERSCORE = auto(),
    SINGLEQUOTE = auto(),
    EOF = auto()
