import os

from magiclog import log
import py.path
from sh import chmod, Command, mkdir

from ..decorators import schemes
from ..err import Err
from .core import DiskLocal, onepath, oneurl, SourceURL, twopaths
from .tar import Tar


class File(DiskLocal, SourceURL):
    """Local files and directories as Arx sources.

    Local file URLs are resolved at the bundling step, allowing vendored
    dependencies and local configuration to be captured and forwarded as part
    of sending an Arx manifest off to be run.

    File URLs are generally absolute paths; but in practice one will want
    paths relative to the Arx manifest file for vendored dependencies and
    relative to the user's home directory for settings. To accommadate this
    need, Arx introduces a virtual directory, ``@``.

    * ``file:///@/./`` refers to the directory in which the Arx manifest file
      is present. Say one wants to reference ``package.json``; this would be
      ``file:///@/./package.json``.

    * The URL ``file:///@/~/`` refers to the user's home directory.

    * The URL ``file:///@/~x/`` refers to the home directory of user ``x`` and
      so on and so forth for every user of the system.

    Now the question arises, what if we have a directory ``@`` at the system
    root? That is what ``file:///@/`` normally refers to. Because ``@`` is a
    reserved character in URIs, a literal interpretation can be forced by
    percent encoding it: ``file:///%40/``.
    """

    @oneurl
    @schemes('file')
    def __init__(self, url):
        self.url = url
        if url.authority != '':
            raise Invalid('Arx can not work with non-local file URLs.')
        self.resolved = py.path.local(handle_at_sign(url.path) or url.path)
        if url.fragment is not None:
            raise Invalid('Arx can not work with plain file URLs that have '
                          'fragments.')

    @property
    def home(self):
        """True if this file URL references home directory with ``~``."""
        return tilde(self.url.path)

    @property
    def dot(self):
        """True if relative to the manifest, using ``.`` or ``..``."""
        return relative(self.url.path)

    @onepath
    def cache(self, cache):
        copy(self.resolved, cache.join('data'))

    @twopaths
    def place(self, cache, path):
        copy(self.resolved, path)

    @onepath
    def run(self, cache, args=[]):
        if not True:
            raise Invalid('Directories can not be run as commands.')
        if self.dot:
            chmod('a+rx', str(self.resolved))
        cmd = Command(str(self.resolved))
        cmd(*args)


class FileTar(Tar, File):
    @oneurl
    @schemes('tar+file')
    def __init__(self, url):
        self.url = url


class Invalid(Err):
    pass


def relative(path):
    return path.startswith('/@/.') or path.startswith('/@/..')


def tilde(path):
    return path.startswith('/@/~')


def handle_at_sign(path):
    if path.startswith('/@/'):
        if relative(path):
            return os.path.abspath(path[3:])
        if tilde(path):
            parts = path.split('/', 3)
            pattern = parts[2]
            home = os.path.expanduser(pattern)
            if home == pattern:
                raise Invalid('No home directory pointed to by: %s', pattern)
            full = os.path.join(home, parts[3]) if len(parts) > 3 else home
            return os.path.abspath(full)
        raise Invalid('Please `/@/` only with `.`, `..` or `~`.')
    return None


def cp(src, dst):
    # If src is a dir, do x
    # If src is not, do y
    pass
