from sh import Command, chmod, cp, curl, mkdir
import uritools

from ..decorators import schemes
from .core import onepath, oneurl, SourceURL, twopaths


class Git(SourceURL):
    """Git respositories as Arx sources.

    These sources have directory nature by default but do support fragments
    to indicate that only certain files or directories should be extracted.

    Query parametes can be used to indicate a particular branch, tag or SHA:

    .. code::

        # Try to find a branch or a tag called beta.
        git+ssh://abc.example.com/web/server.git?beta

        # Same as above.
        git+ssh://abc.example.com/web/server.git?ref=beta

        # Find a SHA beginning with 0abc3df.
        git+ssh://abc.example.com/web/server.git?0abc3df

        # Same as above.
        git+ssh://abc.example.com/web/server.git?ref=0abc3df

    The ``git+ssh://`` and ``git+http://`` schemes are passed, minus the
    leading ``git+``, to ``git``.

    As discussed in :class:`~arx.sources.files.File`, ``git+file:///`` URLs
    can point to repositories in home or the project directory using ``/@/~``
    or ``/@/.`` or ``/@/..``. To reference the Git repository local to the
    manifest, use: ``git+file:///@/.``.
    """

    @oneurl
    @schemes('git+file', 'git+https', 'git+https', 'git+ssh')
    def __init__(self, url):
        self.url = url

    @onepath
    def cache(self, cache):
        raise NotImplementedError()

    @twopaths
    def place(self, cache, path):
        raise NotImplementedError()

    @onepath
    def run(self, cache, args=[]):
        raise NotImplementedError()
