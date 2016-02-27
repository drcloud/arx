#!/usr/bin/env python
import os
import sys

import ptpython.repl

from . import logger
from .logger import log


def main():
    log.info('BEGIN arx;')


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
    # Load module as though user had run ``import arx``, and add the logger.
    ptpython.repl.embed(locals=dict(arx=sys.modules['arx'], log=log),
                        history_filename=history,
                        configure=configure)
    sys.exit(0)


if __name__ == '__main__':
    logger.configure()
    if '--repl' in sys.argv:
        if len(sys.argv) == 2:
            console()
        if '-d' in sys.argv and len(sys.argv) == 3:
            logger.configure(level='debug')
            console()
    main()
