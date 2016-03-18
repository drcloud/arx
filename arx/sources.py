from sh import Command, chmod, cp, curl, mkdir, tar
import py.path
import uritools

from .err import Err
from .signature import signature


class Source(object):
    """ABC for sources."""
    def cache(self, cache):
        raise NotImplementedError()

    def place(self, cache, path):
        raise NotImplementedError()

    def run(self, cache, args=[]):
        raise NotImplementedError()


class Sigs(object):
    """Decorators for argument conversion."""
    init = signature((uritools.SplitResult, uritools.split))
    cache = signature(py.path.local, py.path.local)
    place = signature(py.path.local)
    run = signature(py.path.local)


sigs = Sigs()


class HTTP(Source):
    @sigs.init
    def __init__(self, url):
        self.url = url
        if url.fragment is not None:
            raise Invalid('Arx can not work with plain HTTP/S URLs that have '
                          'fragments.')

    @sigs.cache
    def cache(self, cache):
        headers, body = cache.join('headers'), cache.join('body')
        curl('-sSfL', uritools.uriunsplit(self.url),
             '-D', str(headers), '-o', str(body))

    @sigs.place
    def place(self, cache, path):
        body = cache.join('body')
        mkdir('-p', path.dirname)
        cp(str(body), str(path))

    @sigs.run
    def run(self, cache, args=[]):
        body = cache.join('body')
        chmod('a+rx', str(body))
        cmd = Command(str(body))
        cmd(*args)


class HTTPTar(Source):
    @sigs.init
    def __init__(self, url):
        self.url = url

    @sigs.place
    def place(self, cache, path):
        body = cache.join('body')
        opts = []

        if self.url.fragment is not None:
            slashes = self.url.fragment.count('/')
            n = slashes - 1 if self.url.fragment.endswith('/') else slashes
            if n > 0:
                opts += ['--strip-components', str(n)]
            opts += ['--', self.url.fragment]

        mkdir('-p', path.dirname)
        if self.url.fragment is None or self.url.fragment.endswith('/'):
            tar('-xf', str(body), '-C', str(path), *opts)
        else:
            tar('-xf', str(body), '--to-stdout', *opts, _out=str(path))

    @sigs.run
    def run(self, cache, args=[]):
        program = cache.join('program')
        if self.url.fragment is None:
            raise Invalid('Arx can not execute HTTP/S tarball URLs that have '
                          'no fragment.')
        self.place(cache, program)
        chmod('a+rx', str(program))
        cmd = Command(str(program))
        cmd(*args)


class Invalid(Err):
    pass
