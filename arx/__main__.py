#!/usr/bin/env python
import os
import sys

import ptpython.repl

from . import logger
from .logger import log


def main():
    logger.configure()
    maybe_console()
    log.info('BEGIN arx;')


def include():
    """Inline local file URLs in an Arx file to produce a link-only file."""
    pass


def inline():
    """Inline all URLs in an Arx file to produce a static file."""
    pass


def maybe_console():
    if ['console'] == sys.argv[1:2]:
        if ['-d'] == sys.argv[2:3]:
            logger.configure(level='debug')
        console()
        sys.exit(0)


def console():
    config_dir = os.path.expanduser('~/.ptpython/')
    history = os.path.join(config_dir, 'arx.history')

    # Recycle the user's ptpython configuration.
    def configure(repl):
        path = os.path.join(config_dir, 'config.py')
        if os.path.exists(path):
            ptpython.repl.run_config(repl, unicode(path))

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
