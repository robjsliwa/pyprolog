from prolog.types import Term, Variable, FALSE, Dot, Bar
from prolog.interpreter import Runtime
from prolog.parser import Parser
from prolog.scanner import Scanner


def test_dot_print():
    l1 = str(Dot('A', Dot('B')))
    assert "['A', 'B']" == l1


def test_dot_iterator():
    d = Dot('A', Dot('B', Dot('C')))
    lst = list(d)
    assert lst == ['A', 'B', 'C']


def test_list_with_simple_terms():
    a1_1 = Term('a1')
    a1_2 = Term('a2')

    a2_1 = Term('a1')
    a2_2 = Term('a2')

    l1 = Dot(a1_1, Dot(a1_2))
    l2 = Dot(a2_1, Dot(a2_2))

    m = l1.match(l2)
    assert(m == {})


def test_list_with_vars_and_terms():
    a1_1 = Variable('X')
    a1_2 = Variable('Y')

    a2_1 = Term('a1')
    a2_2 = Term('a2')

    l1 = Dot(a1_1, Dot(a1_2))
    l2 = Dot(a2_1, Dot(a2_2))

    m = l1.match(l2)
    assert(str(m) == '{X: a1, Y: a2}')

    sub = l1.substitute(m)
    assert(str(list(sub)) == '[a1, a2]')


def test_list_with_subset_vars():
    a1_1 = Variable('X')
    a1_2 = Term('a2')

    a2_1 = Term('a1')
    a2_2 = Term('a2')

    l1 = Dot(a1_1, Dot(a1_2))
    l2 = Dot(a2_1, Dot(a2_2))

    m = l1.match(l2)
    assert(str(m) == '{X: a1}')

    sub = l1.substitute(m)
    assert(str(list(sub)) == '[a1, a2]')


def test_list_with_bar_variable_tail():
    a1_1 = Term('a1')
    a1_2 = Term('a2')
    bar_tail = Variable('X')

    a2_1 = Term('a1')
    a2_2 = Term('a2')
    a2_3 = Term('a3')

    l1 = Bar(
        Dot.from_list([a1_1, a1_2]),
        bar_tail
    )
    l2 = Dot.from_list([a2_1, a2_2, a2_3])

    m = l1.match(l2)
    assert(str(m) == '{X: [a3]}')

    sub = l1.substitute(m)
    assert(str(sub) == '[a1, a2 | [a3]]')


def test_list_with_lst_vars_and_tail_vars():
    a1_1 = Variable('X')
    a1_2 = Variable('Y')
    bar_tail = Variable('T')

    a2_1 = Term('a1')
    a2_2 = Term('a2')
    a2_3 = Term('a3')

    l1 = Bar(
        Dot.from_list([a1_1, a1_2]),
        bar_tail
    )
    l2 = Dot.from_list([a2_1, a2_2, a2_3])

    m = l1.match(l2)
    assert(str(m) == '{X: a1, Y: a2, T: [a3]}')

    sub = l1.substitute(m)
    assert(str(sub) == '[a1, a2 | [a3]]')


def test_list_with_head_and_tail_vars():
    head_var = Variable('H')
    bar_tail = Variable('T')

    a2_1 = Term('a1')
    a2_2 = Term('a2')
    a2_3 = Term('a3')

    l1 = Bar(
        Dot.from_list([head_var]),
        bar_tail
    )
    l2 = Dot.from_list([a2_1, a2_2, a2_3])

    m = l1.match(l2)
    assert(str(m) == '{H: a1, T: [a2, a3]}')

    sub = l1.substitute(m)
    assert(str(sub) == '[a1 | [a2, a3]]')


def test_list_with_head_var_and_tail_list():
    head_var = Variable('H')
    tail1 = Variable('X')
    tail2 = Variable('Y')

    a2_1 = Term('a1')
    a2_2 = Term('a2')
    a2_3 = Term('a3')

    l1 = Bar(
        Dot.from_list([head_var]),
        Dot.from_list([tail1, tail2])
    )
    l2 = Dot.from_list([a2_1, a2_2, a2_3])

    m = l1.match(l2)
    assert(str(m) == '{H: a1, X: a2, Y: a3}')

    sub = l1.substitute(m)
    assert(str(sub) == '[a1 | [a2, a3]]')


def test_parser_match_list_with_simple_terms():
    source = '''
    rgb([red, green, blue]).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'rgb([red, green, blue]).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    assert(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)]))  # noqa


def test_parser_bind_list_with_simple_terms():
    source = '''
    rgb([red, green, blue]).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'rgb(X).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    x = goal.args[0]

    # expected_results = [
    #     'location(computer, office)',
    #     'location(chair, office)'
    # ]

    expected_binding = [
        '[red, green, blue]'
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        # assert str(item) == expected_results[index]
        assert str(list(goal.match(item).get(x))) == expected_binding[index]

    assert has_solution is True


def test_parser_match_list_with_wrong_number_of_vars():
    source = '''
    rgb([red, green, blue]).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'rgb([R, G]).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    assert(not(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)])))  # noqa


def test_parser_bind_list_with_vars():
    source = '''
    rgb([red, green, blue]).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'rgb([R, G, B]).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    expected_binding = [
        '{R: red, G: green, B: blue}'
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(goal.match(item)) == expected_binding[index]

    assert has_solution is True


def test_parser_bind_list_with_bar_tail_var():
    source = '''
    rgb([red, green, blue]).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'rgb([red, green | H]).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    expected_binding = [
        '{H: [blue]}'
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(goal.match(item)) == expected_binding[index]

    assert has_solution is True


def test_parser_list_with_head_and_bar_tail_var():
    source = '''
    rgb([red, green, blue]).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'rgb([H | T]).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    expected_binding = [
        '{H: red, T: [green, blue]}'
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(goal.match(item)) == expected_binding[index]

    assert has_solution is True


def test_parser_list_with_head_and_bar_tail_list():
    source = '''
    rgb([red, green, blue]).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'rgb([H | [X, Y]]).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    expected_binding = [
        '{H: red, X: green, Y: blue}'
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(goal.match(item)) == expected_binding[index]

    assert has_solution is True
