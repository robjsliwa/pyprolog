#!/usr/bin/python3

import argparse
import sys
from .interpreter import Runtime
from .repl import run_repl
from .parser import Parser
from .scanner import Scanner


def main():
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
        print('Failed to compile Prolog rules')
        sys.exit()
    run_repl(runtime)


if __name__ == '__main__':
    main()
