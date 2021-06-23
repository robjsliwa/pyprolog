import os
import sys
from colorama import Fore, init
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pathlib import Path
from .parser import Parser
from .scanner import Scanner
from .interpreter import Variable, Rule


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


def run_repl(runtime):
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
            except BufferError as e:
                print(failure(f'Error: {str(e)}'))
    except KeyboardInterrupt:
        print('\nExiting...')
