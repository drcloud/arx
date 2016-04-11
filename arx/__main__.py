#!/usr/bin/env python
import os
import sys

import click
from magiclog import log
import ptpython.repl
import six
import yaml

from .task import Task


def main():
    log.configure()
    maybe_console()
    interpret()


@click.command()
@click.argument('input', type=click.File('rb'))
@click.option('--debug/--no-debug', default=False)
def interpret(input, debug=False):
    """Downloads data and runs commands as per the Arx file."""
    if debug:
        log.configure(level='debug')
    data = yaml.load(input.read())
    task = Task(data)
    task.run()


def maybe_console():
    if ['//console'] == sys.argv[1:2]:
        if ['-d'] == sys.argv[2:3]:
            log.configure(level='debug')
        console()
        sys.exit(0)


def console():
    config_dir = os.path.expanduser('~/.ptpython/')
    history = os.path.join(config_dir, 'arx.history')

    # Recycle the user's ptpython configuration.
    def configure(repl):
        path = os.path.join(config_dir, 'config.py')
        if os.path.exists(path):
            ptpython.repl.run_config(repl, six.u(path))

    if not os.path.isdir(config_dir):          # Ensure config directory exists
        os.mkdir(config_dir)

    if sys.path[0] != '':           # Add the current directory to ``sys.path``
        sys.path.insert(0, '')

    ptpython.repl.enable_deprecation_warnings()
    # Load module as though user had run ``import arx`` and add the logger.
    ptpython.repl.embed(locals=dict(arx=sys.modules['arx'], log=log),
                        history_filename=history,
                        configure=configure)
    sys.exit(0)


if __name__ == '__main__':
    main()
