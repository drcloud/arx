from sh import Command, chmod, curl, mkdir
import uritools

from ..decorators import schemes
from ..err import Err
from .files import File, FileTar
from .jar import Jar
from .core import onepath, oneurl, SourceURL, twopaths
from .tar import Tar


class HTTP(SourceURL):
    """Links to files available over HTTP/S.

    The URL can contain query parameters (``?...``) but not a fragment
    (``#...``). All HTTP URLs are treated as having file nature.
    """

    @oneurl
    @schemes('http', 'https')
    def __init__(self, url):
        self.url = url
        if url.fragment is not None:
            raise Invalid('Arx can not work with plain HTTP/S URLs that have '
                          'fragments.')

    @property
    def base(self):
        # Allows subclasses to inherit this implementation by throwing away the
        # prefix.
        scheme = self.url.scheme.split('+')[-1]
        return self.url._replace(scheme=scheme, fragment=None)

    @twopaths
    def retrieve(self, headers, path):
        # TODO: If `curl` is not present, use urllib.
        curl('-sSfL', uritools.uriunsplit(self.base),
             '-D', str(headers), '-o', str(path))

    @onepath
    def cache(self, cache):
        headers, body = cache.join('headers'), self.dataname(cache)
        self.retrieve(headers, body)
        return File('file:///' + str(body))

    @twopaths
    def place(self, cache, path):
        mkdir('-p', path.dirname)
        self.retrieve('/dev/null', path)

    @onepath
    def run(self, cache, args=[]):
        body = self.dataname(cache)
        chmod('a+rx', str(body))
        cmd = Command(str(body))
        cmd(*args)


class HTTPTar(Tar, HTTP):
    """Links to tar archives available over HTTP/S.

    These URLs have directory nature unless a fragment is passed, as described
    under :class:`~arx.sources.tar.Tar`.
    """

    @oneurl
    @schemes('tar+http', 'tar+https')
    def __init__(self, url):
        self.url = url

    @onepath
    def cache(self, cache):
        # Reuses parent and then rewrites URL.
        as_file = super(HTTPTar, self).cache(cache)
        return FileTar.resolve(as_file.resolved)


class HTTPJar(Jar, HTTP):
    @oneurl
    @schemes('jar+http', 'jar+https')
    def __init__(self, url):
        self.url = url
        if url.fragment is not None:
            raise Invalid('Arx can not handle Jar HTTP/S URLs with fragments.')


class Invalid(Err):
    pass
