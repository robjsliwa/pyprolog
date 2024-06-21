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
from .errors import InterpreterError, ScannerError
from .types import FALSE, CUT, Dot, Bar


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


def display_variables(goal, solution, stream_reader):
    print(stream_reader(), end='')
    has_variables = False
    if isinstance(goal, Rule):
        goal = goal.head
    for arg in goal.args:
        if isinstance(arg, Variable):
            goal_match = goal.match(solution)
            if goal_match:
                bind = goal_match.get(arg)
                print(success(f'{arg} = {bind}'), end=' ')
                has_variables = True
        elif isinstance(arg, Dot):
            goal_match = goal.match(solution)
            if isinstance(arg, Dot) and goal_match:
                for k, v in goal_match.items():
                    if isinstance(k, Variable) and k.name == '_':
                        continue
                    print(f'{k} = {v}', end=' ')
                has_variables = True
        elif isinstance(arg, Bar):
            goal_match = goal.match(solution)
            if goal_match:
                for k, v in goal_match.items():
                    if isinstance(k, Variable) and k.name == '_':
                        continue
                    print(f'{k} = {v}', end=' ')
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
                history=FileHistory(
                    os.path.join(home_path, '.simpleprolog_history')
                ),
                auto_suggest=AutoSuggestFromHistory(),
            )
            if query == '':
                continue

            try:
                goal = Parser(Scanner(query).tokenize()).parse_query()

                runtime.reset_stream()

                is_first_iter = False
                has_solution = False
                for solution in runtime.execute(goal):
                    if isinstance(solution, CUT):
                        break
                    if not isinstance(solution, FALSE):
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
                    display_variables(goal, solution, runtime.stream_read)
                if has_solution:
                    print('yes')
                else:
                    if not is_first_iter:
                        print(runtime.stream_read(), end='')
                    print('no')
            except IndexError:
                print('Unterminated input')
            except KeyboardInterrupt as e:  # Exception as e:
                print(failure(f'Error: {str(e)}'))
            except InterpreterError as e:
                print(failure(f'Error: {str(e)}'))
            except ScannerError as e:
                print(failure(f'Error: {str(e)}'))
    except KeyboardInterrupt:
        print('\nExiting...')
