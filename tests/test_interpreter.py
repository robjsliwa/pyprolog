from prolog.interpreter import Term, Variable, Runtime
from prolog.parser import Parser
from prolog.scanner import Scanner


def test_simple_rule_match():
    known_term = Term('location', Term('computer'), Term('office'))
    x = Variable('X')
    goal = Term('location', Term('computer'), x)
    bindings = goal.match(known_term)
    assert str(bindings) == '{X: office}'
    value = goal.substitute(bindings)
    assert str(value) == 'location(computer, office)'


def test_query_with_multiple_results():
    source = '''
    location(computer, office).
    location(knife, kitchen).
    location(chair, office).
    location(shoe, hall).

    isoffice(X) :- location(computer, X), location(chair, X).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'location(computer, X)'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    x = goal.args[1]

    expected_results = [
        'location(computer, office)',
        'location(chair, office)'
    ]

    expected_binding = [
        'office',
        'chair'
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(item) == expected_results[index]
        assert str(goal.match(item).get(x)) == expected_binding[index]

    assert has_solution is True


def test_puzzle1():
    puzzle = '''
    exists(A, list(A, _, _, _, _)).
    exists(A, list(_, A, _, _, _)).
    exists(A, list(_, _, A, _, _)).
    exists(A, list(_, _, _, A, _)).
    exists(A, list(_, _, _, _, A)).

    rightOf(R, L, list(L, R, _, _, _)).
    rightOf(R, L, list(_, L, R, _, _)).
    rightOf(R, L, list(_, _, L, R, _)).
    rightOf(R, L, list(_, _, _, L, R)).

    middle(A, list(_, _, A, _, _)).

    first(A, list(A, _, _, _, _)).

    nextTo(A, B, list(B, A, _, _, _)).
    nextTo(A, B, list(_, B, A, _, _)).
    nextTo(A, B, list(_, _, B, A, _)).
    nextTo(A, B, list(_, _, _, B, A)).
    nextTo(A, B, list(A, B, _, _, _)).
    nextTo(A, B, list(_, A, B, _, _)).
    nextTo(A, B, list(_, _, A, B, _)).
    nextTo(A, B, list(_, _, _, A, B)).

    puzzle(Houses) :-
        exists(house(red, english, _, _, _), Houses),
        exists(house(_, spaniard, _, _, dog), Houses),
        exists(house(green, _, coffee, _, _), Houses),
        exists(house(_, ukrainian, tea, _, _), Houses),
        rightOf(house(green, _, _, _, _), house(ivory, _, _, _, _), Houses),
        exists(house(_, _, _, oldgold, snails), Houses),
        exists(house(yellow, _, _, kools, _), Houses),
        middle(house(_, _, milk, _, _), Houses),
        first(house(_, norwegian, _, _, _), Houses),
        nextTo(house(_, _, _, chesterfield, _), house(_, _, _, _, fox), Houses),
        nextTo(house(_, _, _, kools, _),house(_, _, _, _, horse), Houses),
        exists(house(_, _, orangejuice, luckystike, _), Houses),
        exists(house(_, japanese, _, parliament, _), Houses),
        nextTo(house(_, norwegian, _, _, _), house(blue, _, _, _, _), Houses),
        exists(house(_, _, water, _, _), Houses),
        exists(house(_, _, _, _, zebra), Houses).

    solution(WaterDrinker, ZebraOwner) :-
        puzzle(Houses),
        exists(house(_, WaterDrinker, water, _, _), Houses),
        exists(house(_, ZebraOwner, _, _, zebra), Houses).
    ''' # noqa

    tokens = Scanner(puzzle).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'solution(WaterDrinker, ZebraOwner)'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    x = goal.args[0]

    expected_results = ['solution(norwegian, japanese)']

    expected_bindings = ['norwegian']

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(item) == expected_results[index]
        assert str(goal.match(item).get(x)) == expected_bindings[index]

    assert has_solution is True


def test_puzzle2():
    puzzle = '''
    exists(A, list(A, _, _, _, _)).
    exists(A, list(_, A, _, _, _)).
    exists(A, list(_, _, A, _, _)).
    exists(A, list(_, _, _, A, _)).
    exists(A, list(_, _, _, _, A)).

    rightOf(R, L, list(L, R, _, _, _)).
    rightOf(R, L, list(_, L, R, _, _)).
    rightOf(R, L, list(_, _, L, R, _)).
    rightOf(R, L, list(_, _, _, L, R)).

    middle(A, list(_, _, A, _, _)).

    first(A, list(A, _, _, _, _)).

    nextTo(A, B, list(B, A, _, _, _)).
    nextTo(A, B, list(_, B, A, _, _)).
    nextTo(A, B, list(_, _, B, A, _)).
    nextTo(A, B, list(_, _, _, B, A)).
    nextTo(A, B, list(A, B, _, _, _)).
    nextTo(A, B, list(_, A, B, _, _)).
    nextTo(A, B, list(_, _, A, B, _)).
    nextTo(A, B, list(_, _, _, A, B)).

    puzzle(Houses) :-
    exists(house(red, british, _, _, _), Houses),
    exists(house(_, swedish, _, _, dog), Houses),
    exists(house(green, _, coffee, _, _), Houses),
    exists(house(_, danish, tea, _, _), Houses),
    rightOf(house(white, _, _, _, _), house(green, _, _, _, _), Houses),
    exists(house(_, _, _, pall_mall, bird), Houses),
    exists(house(yellow, _, _, dunhill, _), Houses),
    middle(house(_, _, milk, _, _), Houses),
    first(house(_, norwegian, _, _, _), Houses),
    nextTo(house(_, _, _, blend, _), house(_, _, _, _, cat), Houses),
    nextTo(house(_, _, _, dunhill, _),house(_, _, _, _, horse), Houses),
    exists(house(_, _, beer, bluemaster, _), Houses),
    exists(house(_, german, _, prince, _), Houses),
    nextTo(house(_, norwegian, _, _, _), house(blue, _, _, _, _), Houses),
    nextTo(house(_, _, _, blend, _), house(_, _, water_, _, _), Houses).

    solution(FishOwner) :-
    puzzle(Houses),
    exists(house(_, FishOwner, _, _, fish), Houses).
    '''

    rules = Parser(
        Scanner(puzzle).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'solution(FishOwner)'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    x = goal.args[0]

    expected_results = ['solution(german)']

    expected_bindings = ['german']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(item) == expected_results[index]
        assert str(goal.match(item).get(x)) == expected_bindings[index]
