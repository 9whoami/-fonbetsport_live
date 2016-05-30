# -*- coding: utf-8 -*-
from os import sys
from argparse import ArgumentParser
from .namespace import argv_var

__prog__ = 'Programm name'
__description__ = ''
__epilog__ = '''(c) April 2016. Автор программы, как всегда,
не несет никакой ответственности ни за что.'''


def create_parser():
    parser = ArgumentParser(prog=__prog__,
                            description=__description__,
                            epilog=__epilog__,
                            add_help=False)
    parser.add_argument('-h', '--help', action='help', help='Справка')

    for key in argv_var:
        parser.add_argument('--{}'.format(key), **argv_var[key])

    return parser.parse_args(sys.argv[1:])
