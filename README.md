# Simple Prolog Interpreter in Python

![badges](https://github.com/robjsliwa/pyprolog/actions/workflows/python-package.yml/badge.svg)
[![license](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

## Set up environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run REPL


```bash
python -m prolog.prolog [options] path
```

For example,

```bash
python -m prolog.prolog tests/data/puzzle1.prolog
```

Sample REPL session output:

```bash
python -m prolog.prolog tests/data/myadven.prolog 

Welcome to Simple Prolog
ctrl-c to quit
> location(desk, office).
yes
> location(desk, office1).
no
> location(X, Y).
X = desk Y = office 
X = apple Y = kitchen 
X = flashlight Y = desk 
X = 'washing machine' Y = cellar 
X = nani Y = 'washing machine' 
X = broccoli Y = kitchen 
X = crackers Y = kitchen 
X = computer Y = office 
no
> door(kitchen, R), location(T, R).
R = office T = desk 
R = office T = computer 
R = cellar T = 'washing machine' 
no
```

Simple Prolog supports following built-ins: write, tab, nl and fail.

You can use them to display values of variables or text:

```
Welcome to Simple Prolog
ctrl-c to quit
> room(X), tab, write(X), nl.
        kitchen
X = kitchen 
        office
X = office 
        hall
X = hall 
        'dinning room'
X = 'dinning room' 
        cellar
X = cellar 
no
>
```

or if you do not want to see the solutions just print out:

```
> write('This is the list of rooms:'), nl, room(X), tab, write(X), nl, fail.
'This is the list of rooms:'
        kitchen
        office
        hall
        'dinning room'
        cellar
no
>
```

You can also perform simple arithmetic operations.  For example given following rule:

```
c_to_f(C, F) :- F is C * 9 / 5 + 32.
```

You can ask Prolog to convert Celsius to Fahrenheit:

```
Welcome to Simple Prolog
ctrl-c to quit
> c_to_f(0, F).
F = 32.0
yes
> c_to_f(100, F).
F = 212.0
yes
>
```

You can also ask Prolog REPL to do calculation directly:

```
Welcome to Simple Prolog
ctrl-c to quit
> Z is 4 * 10 - 2 * 4.
Z = 32.0
yes
> Z is 4 * (10 - 2) * 4.
Z = 128.0
yes
>
```

Following logical operators are supported:

```
==
=/
<
=<
>
>=
```

Here is an example of rule that uses logical operator:

```
freezing(X) :- X =< 32.
```

```
Welcome to Simple Prolog
ctrl-c to quit
> freezing(30).
yes
>
```

Or you can use it directly from REPL:

```
Welcome to Simple Prolog
ctrl-c to quit
> X is 2+2, X > 1.
yes
> X is 2+2, X > 5.
no
>   
```

Simple Prolog also has support for lists.  Here are some examples:

```
Welcome to Simple Prolog
ctrl-c to quit
> rgb([red, green, blue]).
yes
> rgb([R, G, B]).
R = red G = green B = blue 
yes
> rgb([_, G, _]).
G = green 
yes
> rgb([R, green, B]).
R = red B = blue 
yes
> rgb([red, green | H]).
H = [blue] 
yes
> rgb([H | T]).
H = red T = [green, blue] 
yes
> rgb([H | [X, Y]]).
H = red X = green Y = blue 
yes
> 
```

## Test

Linter:

```
python -m flake8
```

Tests:

```
poetry run  pytest --cov=prolog tests
```

## How to Use PyProlog as a Library

Install pyprolog:

```bash
pip install pieprolog
```

Here is an example how to use PyProlog as a library:

```python
from prolog import Scanner, Parser, Runtime


def main():
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

    goal = Parser(Scanner(goal_text).tokenize()).parse_terms()

    x = goal.args[0]

    has_solution = False
    for index, item in enumerate(runtime.execute(goal)):
        has_solution = True
        print(str(item))
        print(str(goal.match(item).get(x)))

    if has_solution:
        print('Query has solution')
    else:
        print('Query has no solution')


if __name__ == "__main__":
    main()
```

## Acknoledgments

This was inspired and based on this [article](https://curiosity-driven.org/prolog-interpreter)

