from sh import Command, chmod, cp, curl, mkdir, tar
import py.path
import uritools

from .err import Err
from .signature import signature
from .schemes import schemes
from .inner.uritools import uridisplay


class Source(object):
    """ABC for sources."""
    def cache(self, cache):
        raise NotImplementedError()

    def place(self, cache, path):
        raise NotImplementedError()

    def run(self, cache, args=[]):
        raise NotImplementedError()

    def __str__(self):
        return uridisplay(self.url)


"""Convert the first argument to a URL."""
oneurl = signature((uritools.SplitResult, uritools.urisplit))
"""Convert the first argument to a parsed path."""
onepath = signature(py.path.local)
"""Convert the first two arguments to parsed paths."""
twopaths = signature(py.path.local, py.path.local)


class HTTP(Source):
    @oneurl
    @schemes('http', 'https')
    def __init__(self, url):
        self.url = url
        if url.fragment is not None:
            raise Invalid('Arx can not work with plain HTTP/S URLs that have '
                          'fragments.')

    @onepath
    def cache(self, cache):
        headers, body = cache.join('headers'), self.data(cache)
        # Allows subclasses, below, to inherit this implementation.
        scheme = self.self.url.scheme.split('+')[-1]
        simplified_url = self.url._replace(scheme=scheme, fragment=None)
        curl('-sSfL', uritools.uriunsplit(simplified_url),
             '-D', str(headers), '-o', str(body))

    @twopaths
    def place(self, cache, path):
        mkdir('-p', path.dirname)
        cp(str(self.data(cache)), str(path))

    @onepath
    def run(self, cache, args=[]):
        body = self.data(cache)
        chmod('a+rx', str(body))
        cmd = Command(str(body))
        cmd(*args)

    @onepath
    def data(self, cache):
        return cache.join('data')


class HTTPTar(HTTP):
    @oneurl
    @schemes('tar+http', 'tar+https')
    def __init__(self, url):
        self.url = url

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
            raise Invalid('Arx can not execute HTTP/S tarball URLs that have '
                          'no fragment.')
        self.place(cache, program)
        chmod('a+rx', str(program))
        cmd = Command(str(program))
        cmd(*args)

    @onepath
    def data(self, cache):
        return cache.join('data.tar')


class HTTPJar(Source):
    @oneurl
    @schemes('jar+http', 'jar+https')
    def __init__(self, url):
        self.url = url
        if url.fragment is not None:
            raise Invalid('Arx can not handle Jar HTTP/S URLs with fragments.')

    @onepath
    def run(self, cache, args=[]):
        cmd = Command('java')
        cmd('-jar', str(self.data(cache)), *args)

    @onepath
    def data(self, cache):
        return cache.join('data.jar')


class Invalid(Err):
    pass
