from contextlib import contextmanager
from tempfile import mkdtemp

from magiclog import log
from sh import rm


@contextmanager
def tmpdir():
    path = mkdtemp(prefix='arx.')
    try:
        log.debug('Temporary directory is: %s', path)
        yield path
    finally:
        rm('-rf', path)
