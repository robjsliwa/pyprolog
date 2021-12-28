from prolog.types import List, Term, Variable


def test_list_with_simple_terms():
    a1_1 = Term('a1')
    a1_2 = Term('a2')

    a2_1 = Term('a1')
    a2_2 = Term('a2')

    l1 = List([a1_1, a1_2])
    l2 = List([a2_1, a2_2])

    m = l1.match(l2)
    assert(m == {})

def test_list_with_vars_and_terms():
    a1_1 = Variable('X')
    a1_2 = Variable('Y')

    a2_1 = Term('a1')
    a2_2 = Term('a2')

    l1 = List([a1_1, a1_2])
    l2 = List([a2_1, a2_2])

    m = l1.match(l2)
    assert(str(m) == '{X: a1, Y: a2}')

    sub = l1.substitute(m)
    assert(str(sub) == '[a1, a2]')

def test_list_with_subset_vars():
    a1_1 = Variable('X')
    a1_2 = Term('a2')

    a2_1 = Term('a1')
    a2_2 = Term('a2')

    l1 = List([a1_1, a1_2])
    l2 = List([a2_1, a2_2])

    m = l1.match(l2)
    assert(str(m) == '{X: a1}')

    sub = l1.substitute(m)
    assert(str(sub) == '[a1, a2]')
