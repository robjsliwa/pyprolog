# Simple Prolog Interpreter in Python

![badges](https://github.com/robjsliwa/pyprolog/actions/workflows/python-package.yml/badge.svg)
[![license](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

## Install dependencies

```
poetry install
```

## Run REPL

Using poetry:

```
poetry run prolog [options] path
```

or

```
python -m prolog.prolog [options] path
```

For example,

```
poetry run prolog tests/data/puzzle1.prolog
```

Sample REPL session output:

```
poetry run prolog tests/data/myadven.prolog 

Welcome to Simple Prolog
ctrl-c to quit
> location(desk, office)
yes
> location(desk, office1)
no
> location(X, Y)
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

## Test

Linter:

```
poetry run flake8
```

Tests:

```
poetry run  pytest --cov=prolog tests
```

## Acknoledgments

This was inspired and based on this [article](https://curiosity-driven.org/prolog-interpreter)

