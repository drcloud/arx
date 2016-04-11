from sh import Command, chmod, cp, curl, mkdir
import uritools

from ..decorators import schemes
from ..err import Err
from .jar import Jar
from .core import onepath, oneurl, SourceURL, twopaths
from .tar import Tar


class HTTP(SourceURL):
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
        # Allows subclasses to inherit this implementation by throwing away the
        # prefix.
        scheme = self.url.scheme.split('+')[-1]
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


class HTTPTar(Tar, HTTP):
    @oneurl
    @schemes('tar+http', 'tar+https')
    def __init__(self, url):
        self.url = url


class HTTPJar(Jar, HTTP):
    @oneurl
    @schemes('jar+http', 'jar+https')
    def __init__(self, url):
        self.url = url
        if url.fragment is not None:
            raise Invalid('Arx can not handle Jar HTTP/S URLs with fragments.')


class Invalid(Err):
    pass
