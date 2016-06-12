import py.path
import uritools

from ..decorators import signature
from ..inner.uritools import uridisplay


class Source(object):
    """ABC for sources."""
    def cache(self, cache):
        """Generates a filesystem local source from this source.

        The :class:`~arx.sources.files.File` thus returned can be used in place
        of the original source.

        The method is passed a created, temporary directory which is cleared
        by the implementation. The :class:`~arx.sources.files.File` source
        should be stored somewhere under this directory, but it is allowed to
        store metadata, like checksums, alongside it.

        It is advisable that this method reuse data when it is already present
        in the cache; but this is not a requirement. An implementation that
        clears the cache and pulls the data anew each time will not break
        clients.

        For :class:`~arx.sources.files.File` and its subclasses, ``cache``
        returns ``self``.
        """
        raise NotImplementedError()

    def place(self, cache, path):
        raise NotImplementedError()

    def run(self, cache, args=[]):
        raise NotImplementedError()

    def externalize(self):
        """Provide a representation of a source in terms of simple data types:
           strings, lists and dictionaries.

        For most sources, this will be a string representing a URL. For
        :class:`arx.sources.inline.Inline` sources, this will be a dictionary
        with one K/V pair, where both K and V are strings.
        """
        raise NotImplementedError()


class DiskLocal(Source):
    """Sources that are on local disk."""
    pass


class SourceURL(Source):
    def __str__(self):
        return uridisplay(self.url)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, str(self))

    def __getattr__(self, name):
        return getattr(self.url, name)

    def externalize(self):
        return uritools.uriunsplit(self.url)

    def dataname(self, cache):
        """Default name for data stored in the cache."""
        return cache.join('data')


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
