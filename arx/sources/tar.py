from sh import chmod, Command, mkdir, tar

from ..err import Err
from .core import twopaths, onepath


class Tar(object):
    """
    With ``tar+...`` type URLs, passing fragment can give the source file
    nature; but by default it has directory nature.

    A fragment can reference a subdirectory or a particular file in the
    archive; in the latter case, the URL can be treated as a runnable program.

    There is a convention with release tarballs, to have a single top-level
    directory that is named something like ``<project>-<version>``. Tar offers
    ``--strip-components`` for this situation, where the archive is expanded
    as though only the top-level directory had been asked for. To access this
    functionality, use ``#/`` (this is the same as ``--strip-components 1``).
    Supplying ``#//`` would expand from all second-level directories (of which
    there is hopefully only one), &c.
    """

    @twopaths
    def place(self, cache, path):
        data = self.data(cache)
        opts = []

        if self.url.fragment is not None:
            slashes = self.url.fragment.count('/')
            n = slashes - 1 if self.url.fragment.endswith('/') else slashes
            if n > 0:
                opts += ['--strip-components', str(n)]
            opts += ['--', self.url.fragment]

        mkdir('-p', path.dirname)
        if self.url.fragment is None or self.url.fragment.endswith('/'):
            tar('-xf', str(data), '-C', str(path), *opts)
        else:
            tar('-xf', str(data), '--to-stdout', *opts, _out=str(path))

    @onepath
    def run(self, cache, args=[]):
        program = cache.join('program')
        if self.url.fragment is None:
            raise Invalid('Arx can not execute tarball URLs that have no '
                          'fragment.')
        self.place(cache, program)
        chmod('a+rx', str(program))
        cmd = Command(str(program))
        cmd(*args)

    @onepath
    def data(self, cache):
        return cache.join('data.tar')


class Invalid(Err):
    pass
