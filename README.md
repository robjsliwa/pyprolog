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

