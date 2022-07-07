from prolog.interpreter import Runtime
from prolog.parser import Parser
from prolog.scanner import Scanner
from prolog.types import Term


def color_predicate():
    colors = ['red', 'green', 'blue']
    for color in colors:
        yield Term(color)


def test_simple_predicate_function():
    source = '''
    rgb(red, green, blue).
    color1(grey).
    color2(grey, white).
    nocolor.
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    runtime.register_function(color_predicate, 'color', 1)

    goal_text = 'color(Color).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    expected_binding = [
        '{Color: red}',
        '{Color: gree}',
        '{Color: blue}'
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(goal.match(item)) == expected_binding[index]

    assert has_solution is True
