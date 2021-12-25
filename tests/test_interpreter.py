from prolog.interpreter import Runtime, Rule
from prolog.types import Variable, Term, FALSE, TRUE, CUT
from prolog.parser import Parser
from prolog.scanner import Scanner
import cProfile
import functools
import pstats
import tempfile


def profile_me(func):
    @functools.wraps(func)
    def wraps(*args, **kwargs):
        file = tempfile.mktemp()
        profiler = cProfile.Profile()
        profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(file)
        metrics = pstats.Stats(file)
        metrics.strip_dirs().sort_stats('time').print_stats(100)
    return wraps


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

    goal_text = 'location(X, office).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_terms()

    x = goal.args[0]

    expected_results = [
        'location(computer, office)',
        'location(chair, office)'
    ]

    expected_binding = [
        'computer',
        'chair'
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(item) == expected_results[index]
        assert str(goal.match(item).get(x)) == expected_binding[index]

    assert has_solution is True


def test_multi_term_query():
    source = '''
    location(desk, office).
    location(apple, kitchen).
    location(flashlight, desk).
    location('washing machine', cellar).
    location(nani, 'washing machine').
    location(broccoli, kitchen).
    location(crackers, kitchen).
    location(computer, office).

    door(office, hall).
    door(kitchen, office).
    door(hall, 'dinning room').
    door(kitchen, cellar).
    door('dinninr room', kitchen).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'door(kitchen, R), location(T, R).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    R = goal.head.args[0]
    T = goal.head.args[1]

    expected_binding = [
        {'R': 'office', 'T': 'desk'},
        {'R': 'office', 'T': 'computer'},
        {'R': 'cellar', 'T': "washing machine"}
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(goal.head.match(item).get(R)) == \
            expected_binding[index]['R']
        assert str(goal.head.match(item).get(T)) == \
            expected_binding[index]['T']

    assert has_solution is True


def test_query_with_builtins():
    source = '''
    room(kitchen).
    room(office).
    room(hall).
    room('dinning room').
    room(cellar).

    location(desk, office).
    location(apple, kitchen).
    location(flashlight, desk).
    location('washing machine', cellar).
    location(nani, 'washing machine').
    location(broccoli, kitchen).
    location(crackers, kitchen).
    location(computer, office).

    door(office, hall).
    door(kitchen, office).
    door(hall, 'dinning room').
    door(kitchen, cellar).
    door('dinninr room', kitchen).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'room(X), tab, write(X), nl.'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    X = goal.head.args[0]

    expected_binding = [
        {'X': 'kitchen'},
        {'X': 'office'},
        {'X': 'hall'},
        {'X': "dinning room"},
        {'X': 'cellar'}
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        assert str(goal.head.match(item).get(X)) == \
            expected_binding[index]['X']

    assert has_solution is True


def test_fail_builtin():
    source = '''
    room(kitchen).
    room(office).
    room(hall).
    room('dinning room').
    room(cellar).

    location(desk, office).
    location(apple, kitchen).
    location(flashlight, desk).
    location('washing machine', cellar).
    location(nani, 'washing machine').
    location(broccoli, kitchen).
    location(crackers, kitchen).
    location(computer, office).

    door(office, hall).
    door(kitchen, office).
    door(hall, 'dinning room').
    door(kitchen, cellar).
    door('dinninr room', kitchen).
    '''

    tokens = Scanner(source).tokenize()
    rules = Parser(tokens).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'room(X), tab, write(X), nl, fail.'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    X = goal.head.args[0]

    expected_binding = [
        {'X': 'kitchen'},
        {'X': 'office'},
        {'X': 'hall'},
        {'X': "'dinning room'"},
        {'X': 'cellar'}
    ]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        if not isinstance(item, FALSE):
            has_solution = True
            assert str(goal.head.match(item).get(X)) == \
                expected_binding[index]['X']

    assert has_solution is False


@profile_me
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

    goal_text = 'solution(WaterDrinker, ZebraOwner).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

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

    goal_text = 'solution(FishOwner).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[0]

    expected_results = ['solution(german)']

    expected_bindings = ['german']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(item) == expected_results[index]
        assert str(goal.match(item).get(x)) == expected_bindings[index]


def test_support_for_numbers():
    input = '''
    window(main, 2, 2.0, 20, 72).
    window(error, 15, 4.0, 20, 78).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = 'window(T, X, X, Z, W).'

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[1]

    expected_results = ['window(main, 2.0, 2.0, 20.0, 72.0)']

    expected_bindings = ['2.0']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(item) == expected_results[index]
        assert str(goal.match(item).get(x)) == expected_bindings[index]


def test_support_for_string_literals():
    input = '''
    customer('John Jones', boston, good_credit).
    customer('Sally Smith', chicago, good_credit).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "customer('Sally Smith', Y, Z)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[1]

    expected_results = ["customer(Sally Smith, chicago, good_credit)"]

    expected_bindings = ['chicago']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(item) == expected_results[index]
        assert str(goal.match(item).get(x)) == expected_bindings[index]


def test_simple_arithmetics():
    input = '''
    test(Y) :- Y is 5 + 2 * 3 - 1.
    test2(Z) :- Z is (5 + 2) * (3 - 1).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "test(Y)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[0]

    expected_bindings = ['10.0']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(goal.match(item).get(x)) == expected_bindings[index]


def test_arithmetics_with_grouping():
    input = '''
    test(Z) :- Z is (5 + 2) * (3 - 1).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "test(Y)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[0]

    expected_bindings = ['14.0']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(goal.match(item).get(x)) == expected_bindings[index]


def test_arithmetics_with_variables():
    input = '''
    c_to_f(C, F) :- F is C * 9 / 5 + 32.
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "c_to_f(100, X)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[1]

    expected_bindings = ['212.0']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(goal.match(item).get(x)) == expected_bindings[index]

    goal_text = "c_to_f(0, X)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[1]

    expected_bindings = ['32.0']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(goal.match(item).get(x)) == expected_bindings[index]


def test_arithmetics_with_variables_same_as_rule():
    input = '''
    c_to_f(C, F) :- F is C * 9 / 5 + 32.
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "c_to_f(100, F)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[1]

    expected_bindings = ['212.0']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(goal.match(item).get(x)) == expected_bindings[index]

    goal_text = "c_to_f(0, F)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[1]

    expected_bindings = ['32.0']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(goal.match(item).get(x)) == expected_bindings[index]


def test_logic_equal():
    input = '''
    sum_eq_4(Y) :- X is Y + 2, X == 4.
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "sum_eq_4(2)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(
        len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)]))  # noqa

    goal_text = "sum_eq_4(3)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(
        not(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)])))  # noqa


def test_logic_not_equal():
    input = '''
    sum_eq_4(Y) :- X is Y + 2, X =/ 4.
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "sum_eq_4(3)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(len([s for s in runtime.execute(goal)if not isinstance(s, FALSE)]))  # noqa

    goal_text = "sum_eq_4(2)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(not(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)])))  # noqa


def test_logic_greater():
    input = '''
    sum_4(Y) :- X is Y + 2, X > 4.
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "sum_4(3)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)]))  # noqa

    goal_text = "sum_4(2)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(not(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)])))  # noqa


def test_logic_greater_or_equal():
    input = '''
    sum_4(Y) :- X is Y + 2, X >= 4.
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "sum_4(3)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)]))  # noqa

    goal_text = "sum_4(2)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)]))  # noqa

    goal_text = "sum_4(1)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(not(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)])))  # noqa


def test_logic_less():
    input = '''
    sum_4(Y) :- X is Y + 2, X < 4.
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "sum_4(1)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)]))  # noqa

    goal_text = "sum_4(2)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(not(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)])))  # noqa


def test_logic_less_or_equal():
    input = '''
    sum_4(Y) :- X is Y + 2, X =< 4.
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "sum_4(1)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)]))  # noqa

    goal_text = "sum_4(2)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)]))  # noqa

    goal_text = "sum_4(3)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(not(len([s for s in runtime.execute(goal) if not isinstance(s, FALSE)])))  # noqa


def test_insert_rule_left():
    input = '''
    block(a).

    room(kitchen).
    room(hallway).
    room('dinning room').

    location(table, kitchen).
    location(chair, 'dinning room').

    here(kitchen).

    take(X) :- here(Y), location(X, Y).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    head = Term('room', Term('bathroom'))
    room_rule = Rule(head, TRUE())
    runtime.insert_rule_left(room_rule)

    assert(room_rule == runtime.rules[1])


def test_insert_rule_right():
    input = '''
    block(a).

    room(kitchen).
    room(hallway).
    room('dinning room').

    location(table, kitchen).
    location(chair, 'dinning room').

    here(kitchen).

    take(X) :- here(Y), location(X, Y).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    head = Term('room', Term('bathroom'))
    room_rule = Rule(head, TRUE())
    runtime.insert_rule_right(room_rule)

    assert(room_rule == runtime.rules[4])


def test_remove_rule():
    input = '''
    block(a).

    room(kitchen).
    room(hallway).
    room(bathroom).
    room('dinning room').

    location(table, kitchen).
    location(chair, 'dinning room').

    here(kitchen).

    take(X) :- here(Y), location(X, Y).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)
    original_rules_len = len(runtime.rules)

    goal_text = "room(bathroom)."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(list(runtime.execute(goal)))

    head = Term('room', Term('bathroom'))
    room_rule = Rule(head, TRUE())
    runtime.remove_rule(room_rule)

    assert(original_rules_len - 1 == len(runtime.rules))

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(not(list(runtime.execute(goal))))


def test_remove_complex_rule():
    input = '''
    block(a).

    room(kitchen).
    room(hallway).
    room(bathroom).
    room('dinning room').

    location(table, kitchen).
    location(chair, 'dinning room').

    here(kitchen).

    take(X) :- here(Y), location(X, Y).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)
    original_rules_len = len(runtime.rules)

    goal_text = "take(X)."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(list(runtime.execute(goal)))

    head = Term('take', Variable('X'))
    take_rule = Rule(head, TRUE())
    runtime.remove_rule(take_rule)

    assert(original_rules_len - 1 == len(runtime.rules))

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(not(list(runtime.execute(goal))))


def test_retract_rule():
    input = '''
    block(a).

    room(kitchen).
    room(hallway).
    room(bathroom).
    room('dinning room').

    location(table, kitchen).
    location(chair, 'dinning room').

    here(kitchen).

    take(X) :- here(Y), location(X, Y).
    disappear :- retract(here(_)).
    move(Place) :- retract(here(_)), asserta(here(Place)).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)
    original_rules_len = len(runtime.rules)

    goal_text = "disappear."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()
    assert(list(runtime.execute(goal)))
    assert(original_rules_len - 1 == len(runtime.rules))

    goal_text = "here(kitchen)."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(not(list(runtime.execute(goal))))


def test_retract_and_asserta_rule():
    input = '''
    block(a).

    room(kitchen).
    room(hallway).
    room(bathroom).
    room('dinning room').

    location(table, kitchen).
    location(chair, 'dinning room').

    here(kitchen).

    take(X) :- here(Y), location(X, Y).
    disappear :- retract(here(_)).
    move(Place) :- retract(here(_)), asserta(here(Place)).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)
    original_rules_len = len(runtime.rules)

    goal_text = "move(office)."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()
    assert(list(runtime.execute(goal)))
    assert(original_rules_len == len(runtime.rules))

    goal_text = "here(kitchen)."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(not(list(runtime.execute(goal))))

    goal_text = "here(office)."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(list(runtime.execute(goal)))


def test_assertz_rule():
    input = '''
    block(a).

    room(kitchen).
    room(hallway).
    room(bathroom).
    room('dinning room').

    location(table, kitchen).
    location(chair, 'dinning room').

    here(kitchen).

    take(X) :- here(Y), location(X, Y).
    appear :- assertz(block(b)).
    move(Place) :- retract(here(_)), asserta(here(Place)).
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)
    original_rules_len = len(runtime.rules)

    goal_text = "appear."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()
    assert(list(runtime.execute(goal)))
    assert(original_rules_len + 1 == len(runtime.rules))

    goal_text = "block(b)."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(list(runtime.execute(goal)))

    goal_text = "block(X)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[0]

    expected_results = ['block(a)', 'block(b)']

    expected_bindings = ['a', 'b']

    for index, item in enumerate(runtime.execute(goal)):
        assert str(item) == expected_results[index]
        assert str(goal.match(item).get(x)) == expected_bindings[index]


def test_cut_predicate():
    input = '''
    data(one).
    data(two).
    data(three).

    cut_test_a(X) :-
    data(X).
    cut_test_a('last clause').

    cut_test_b(X) :-
    data(X),
    !.
    cut_test_b('last clause').
    '''

    rules = Parser(
        Scanner(input).tokenize()
    ).parse_rules()

    runtime = Runtime(rules)

    goal_text = "cut_test_a(X)."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()
    assert(list(runtime.execute(goal)))

    x = goal.args[0]

    expected_results = [
        'cut_test_a(one)',
        'cut_test_a(two)',
        'cut_test_a(three)',
        'cut_test_a(last clause)'
    ]

    expected_bindings = [
        'one',
        'two',
        'three',
        'last clause'
    ]

    for index, item in enumerate(runtime.execute(goal)):
        assert str(item) == expected_results[index]
        assert str(goal.match(item).get(x)) == expected_bindings[index]

    goal_text = "cut_test_b(X)."
    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    assert(list(runtime.execute(goal)))

    goal_text = "cut_test_b(X)."

    goal = Parser(
        Scanner(goal_text).tokenize()
    ).parse_query()

    x = goal.args[0]

    expected_results = ['cut_test_b(one)']

    expected_bindings = ['one']

    for index, item in enumerate(runtime.execute(goal)):
        if not isinstance(item, CUT):
            print(f'ITEM: {item}')
            print(f'{item} == {expected_results[index]}')
            print(f'{goal.match(item).get(x)} == {expected_bindings[index]}')
            assert str(item) == expected_results[index]
            assert str(goal.match(item).get(x)) == expected_bindings[index]
