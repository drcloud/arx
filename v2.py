#!/usr/bin/env python
from contextlib import contextmanager
import errno
import inspect
import os
import pkg_resources
from subprocess import check_output, CalledProcessError


class Version(object):
    def __init__(self, default='0', version_file='VERSION'):
        self._version = None
        self.default = default
        self.version_file = version_file

    @property
    def version(self):
        if self._version is not None:
            return self._version.strip()

    def imprint(self, path=None):
        """Write the determined version, if any, to ``self.version_file`` or
           the path passed as an argument.
        """
        if self.version is not None:
            with open(path or self.version_file, 'w') as h:
                h.write(self.version + '\n')
        else:
            raise ValueError('Can not write null version to file.')
        return self

    def from_file(self, path=None):
        """Look for a version in ``self.version_file``, or in the specified
           path if supplied.
        """
        if self._version is None:
            self._version = file_version(path or self.version_file)
        return self

    def from_default(self):
        if self._version is None:
            self._version = self.default
        return self

    def from_git(self, path=None):
        """Use Git to determine the package version.

           This routine uses the __file__ value of the caller to determine
           which Git repository root to use.
        """
        if self._version is None:
            frame = caller(1)
            path = frame.f_globals.get('__file__') or '.'
            try:
                with cd(path):
                    self._version = git_version()
            except CalledProcessError:
                pass
        return self

    def from_pkg(self):
        """Use pkg_resources to determine the installed package version.
        """
        if self._version is None:
            frame = caller(1)
            pkg = frame.f_globals.get('__package__')
            if pkg is not None:
                self._version = pkg_version(pkg)
        return self

    def from_fn(self, fn):
        if self._version is None:
            self._version = fn()
        return self


v2 = Version()


def file_version(name='VERSION'):
    if os.path.exists(name):
        with open(name) as h:
            txt = h.read().strip()
            if len(txt) != 0:
                return s(txt)


def pkg_version(package=None):
    try:
        s(pkg_resources.get_distribution(package).version)
    except:
        pass


def git_version():
    """Constructs a version string of the form:

           <tag>[.<distance-from-tag>[+<branch-name-if-not-master>]]

       Master is understood to be always buildable and thus untagged
       versions are treated as patch levels. Branches not master are treated
       as PEP-440 "local version identifiers".
    """
    tag = check_output(['git', 'describe']).strip()
    pieces = s(tag).split('-')
    dotted = pieces[0]
    if len(pieces) < 2:
        distance = None
    else:
        # Distance from the latest tag is treated as a patch level.
        distance = pieces[1]
        dotted += '.' + s(distance)
    # Branches that are not master are treated as local:
    #   https://www.python.org/dev/peps/pep-0440/#local-version-identifiers
    if distance is not None:
        branch = check_output(['git', 'rev-parse',
                               '--abbrev-ref', 'HEAD']).strip()
        if branch != 'master':
            dotted += '+' + s(branch)
    return dotted


@contextmanager
def cd(path='.'):
    cwd = os.path.abspath(os.getcwd())
    try:
        try:
            os.chdir(path)
        except OSError as e:
            if e.errno != errno.ENOTDIR:
                raise
            d = os.path.dirname(path)
            os.chdir('.' if d == '' else d)
        yield
    finally:
        os.chdir(cwd)


def caller(height=0):
    caller = inspect.stack()[height+1]
    return caller[0]


def s(something):
    if isinstance(something, str):
        return something
    return something.decode()
