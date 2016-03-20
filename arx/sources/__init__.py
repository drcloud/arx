import py.path
import uritools

from ..inner.uritools import uridisplay
from ..decorators import signature


class Source(object):
    """ABC for sources."""
    def cache(self, cache):
        raise NotImplementedError()

    def place(self, cache, path):
        raise NotImplementedError()

    def run(self, cache, args=[]):
        raise NotImplementedError()

    def inline(self):
        """Returns None to indicate no inlining is needed."""
        return None

    def sign(self):
        """Returns None to indicate no signing is needed."""
        return None


class SourceURL(Source):
    def __str__(self):
        return uridisplay(self.url)

    def __getattr__(self, name):
        return getattr(self.url, name)


"""Convert the first argument to a URL."""
oneurl = signature((uritools.SplitResult, uritools.urisplit))
"""Convert the first argument to a parsed path."""
onepath = signature(py.path.local)
"""Convert the first two arguments to parsed paths."""
twopaths = signature(py.path.local, py.path.local)
