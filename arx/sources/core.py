import py.path
import uritools

from ..decorators import signature
from ..inner.uritools import uridisplay


class Source(object):
    """ABC for sources."""
    def cache(self, cache):
        raise NotImplementedError()

    def place(self, cache, path):
        raise NotImplementedError()

    def run(self, cache, args=[]):
        raise NotImplementedError()

    def externalize(self):
        """Provide a data representation in terms of simple data types:
           strings, sequences and dictionaries."""
        raise NotImplementedError()


class DiskLocal(Source):
    """Sources that are on local disk."""
    def delocalize(self):
        """Returns a new, non-local ``Source``."""
        raise NotImplementedError()


class SourceURL(Source):
    def __str__(self):
        return uridisplay(self.url)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, str(self))

    def __getattr__(self, name):
        return getattr(self.url, name)

    def externalize(self):
        return uritools.uriunsplit(self.url)


class SignableURL(SourceURL):
    """URLs that can be signed to allow privileged access without granting
       credentials. For example, signing S3 URLs to get HTTP URLs."""
    def sign(self):
        """Returns a new signed ``Source``."""
        raise NotImplementedError()


"""Convert the first argument to a URL."""
oneurl = signature((uritools.SplitResult, uritools.urisplit))
"""Convert the first argument to a parsed path."""
onepath = signature(py.path.local)
"""Convert the first two arguments to parsed paths."""
twopaths = signature(py.path.local, py.path.local)
