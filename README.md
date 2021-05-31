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

