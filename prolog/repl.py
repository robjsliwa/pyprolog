import argparse
import sys
from colorama import Fore, init
from .parser import Parser, lexer
from .interpreter import Runtime


init(autoreset=True)


def success(input):
    return f'{Fore.GREEN}{input}'


def failure(input):
    return f'{Fore.RED}{input}'


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

        rules = Parser(lexer(rules_text)).parse_rules()
        runtime = Runtime(rules)
    except Exception as e:
        print(f'Error while loading rules: {str(e)}')
        sys.exit()

    if runtime is None:
        print(failure('Failed to compile Prolog rules'))
        sys.exit()

    try:
        while True:
            query = input('>>> ')
            try:
                goal = Parser(lexer(query)).parse_terms()
                for index, item in enumerate(runtime.execute(goal)):
                    print(success(item))
            except Exception as e:
                print(failure(f'Error: {str(e)}'))
    except KeyboardInterrupt:
        print('\nExiting...')
