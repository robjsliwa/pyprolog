import argparse
import os
import sys
from colorama import Fore, init
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pathlib import Path
from .parser import Parser
from .scanner import Scanner
from .interpreter import Runtime


init(autoreset=True)

home_path = str(Path.home())


def success(input):
    return f'{Fore.GREEN}{input}'


def failure(input):
    return f'{Fore.RED}{input}'


def warning(input):
    return f'{Fore.YELLOW}{input}'


def run_repl():
    ap = argparse.ArgumentParser(
        prog='prolog',
        usage='%(prog)s [options] path',
        description='Simple Prolog interpreter'
    )
    ap.add_argument(
        'Path',
        type=str,
        help='Path to file with Prolog rules'
    )
    args = ap.parse_args()
    input_path = args.Path

    rules_text = ''
    runtime = None
    try:
        with open(input_path) as reader:
            line = reader.readline()
            while line != '':
                rules_text += line
                line = reader.readline()

        rules = Parser(
            Scanner(rules_text).tokenize()
        ).parse_rules()
        runtime = Runtime(rules)
    except Exception as e:
        print(f'Error while loading rules: {str(e)}')
        sys.exit()

    if runtime is None:
        print(failure('Failed to compile Prolog rules'))
        sys.exit()

    print(success('\nWelcome to Simple Prolog'))
    print(warning('ctrl-c to quit'))
    try:
        while True:
            query = prompt(
                '> ',
                history=FileHistory(os.path.join(
                    home_path, '.simpleprolog_history')),
                auto_suggest=AutoSuggestFromHistory()
            )
            try:
                goal = Parser(
                    Scanner(query).tokenize()
                ).parse_terms()
                for index, item in enumerate(runtime.execute(goal)):
                    print(success(item))
            except Exception as e:
                print(failure(f'Error: {str(e)}'))
    except KeyboardInterrupt:
        print('\nExiting...')
