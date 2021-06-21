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
from .interpreter import Runtime, Variable, Rule


init(autoreset=True)

home_path = str(Path.home())


if os.name == 'nt':
    import msvcrt

    def wait_for_char():
        return msvcrt.getch().decode()
else:
    import tty
    import termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    def wait_for_char():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def success(input):
    return f'{Fore.GREEN}{input}'


def failure(input):
    return f'{Fore.RED}{input}'


def warning(input):
    return f'{Fore.YELLOW}{input}'


def display_variables(goal, solution):
    has_variables = False
    if isinstance(goal, Rule):
        goal = goal.head
    for index, arg in enumerate(goal.args):
        if isinstance(arg, Variable):
            v = goal.args[index]
            bind = goal.match(solution).get(v)
            print(success(f'{arg} = {bind}'), end=' ')
            has_variables = True
    if has_variables:
        print('')


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
    except Exception:
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
                ).parse_query()

                is_first_iter = False
                has_solution = False
                for solution in runtime.execute(goal):
                    has_solution = True
                    if is_first_iter is False:
                        is_first_iter = True
                    else:
                        ch = wait_for_char()
                        if ch == ';':
                            has_solution = False
                        else:
                            has_solution = False
                            break
                    display_variables(goal, solution)
                if has_solution:
                    print('yes')
                else:
                    print('no')
            except Exception as e:
                print(failure(f'Error: {str(e)}'))
    except KeyboardInterrupt:
        print('\nExiting...')
