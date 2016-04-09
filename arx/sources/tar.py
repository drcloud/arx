from sh import chmod, Command, mkdir, tar

from ..err import Err
from .core import twopaths, onepath


class Tar(object):
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
