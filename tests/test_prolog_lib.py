from prolog.interpreter import Runtime
from prolog.parser import Parser
from prolog.scanner import Scanner


class SomeObject:
    def __init__(self, name, color, size):
        self.name = name
        self.color = color
        self.size = size


def test_lib_struct():
    some_obj = SomeObject(
        'TestObject',
        'blue',
        10
    )
