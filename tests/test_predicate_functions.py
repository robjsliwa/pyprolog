from prolog.interpreter import Runtime
from prolog.parser import Parser
from prolog.scanner import Scanner
from prolog.types import Term


def color_predicate():
    colors = ['red', 'green', 'blue']
    for color in colors:
        yield Term(color)


def point_predicate():
    points = [(1, 1), (2, 2), (3, 3)]
    for point in points:
        yield Term(point[0]), Term(point[1])


def hpos_predicate():
    hpositions = [(10, 10), (20, 20), (30, 30)]
    for point in hpositions:
        yield Term(point[0]), Term(point[1])


def vpos_predicate():
    vpositions = [(1, 1), (2, 2), (3, 3)]
    for point in vpositions:
        yield Term(point[0]), Term(point[1])


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


def test_two_variable_predicate_function():
    source = '''
    rgb(red, green, blue).
    color1(grey).
    color2(grey, white).
    nocolor.
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    runtime.register_function(point_predicate, 'point', 2)

    goal_text = 'point(X, Y).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    expected_binding = [
        '{X: 1, Y: 1}',
        '{X: 2, Y: 2}',
        '{X: 3, Y: 3}'
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(goal.match(item)) == expected_binding[index]

    assert has_solution is True


def test_two_predicate_functions():
    source = '''
    box_pos(X1, Y1, X2, Y2) :- hpos(Y1, Y2), vpos(X1, X2).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    runtime.register_function(hpos_predicate, 'hpos', 2)
    runtime.register_function(vpos_predicate, 'vpos', 2)

    goal_text = 'box_pos(X1, Y1, X2, Y2).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    expected_binding = [
        '{X1: 1, Y1: 10, X2: 1, Y2: 10}',
        '{X1: 2, Y1: 20, X2: 2, Y2: 20}',
        '{X1: 3, Y1: 30, X2: 3, Y2: 30}'
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(goal.match(item)) == expected_binding[index]

    assert has_solution is True
