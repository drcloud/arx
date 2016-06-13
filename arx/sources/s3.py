import boto3
from sh import Command, chmod, cp, mkdir, rsync
import uritools

from ..decorators import schemes
from ..err import Err
from .files import File, FileTar
from .http import HTTP, HTTPTar, HTTPJar
from .jar import Jar
from .core import onepath, oneurl, SignableURL, twopaths
from .tar import Tar


class S3(SignableURL):
    """Links objects in S3.

    The URL can end with a ``/`` to give it directory nature; otherwise it has
    file nature. With directory nature, the directory is unpacked recursively.
    """

    @oneurl
    @schemes('s3')
    def __init__(self, url):
        self.url = url
        if url.fragment is not None:
            raise Invalid('Arx can not work with plain S3 URLs that have '
                          'fragments.')

    @property
    def dirlike(self):
        return self.url.path.endswith('/')

    @property
    def base(self):
        # Allows subclasses to inherit this implementation by throwing away the
        # prefix.
        scheme = self.url.scheme.split('+')[-1]
        return self.url._replace(scheme=scheme, fragment=None)

    def signed_get(self, seconds=3600):
        if self.dirlike:
            raise Invalid('Not able to sign directory-like S3 URLs.')
        data = dict(Bucket=self.url.host, Key=self.url.path)
        s3 = boto3.client('s3')
        link = s3.generate_presigned_url('get_object', data, ExpiresIn=seconds)
        return link

    def sign(self):
        return HTTP(self.signed_get())

    @onepath
    def cache(self, cache):
        data = self.dataname(cache)
        cmd = Command('aws')
        sub = 'sync' if self.dirlike else 'cp'
        cmd('s3', sub, uritools.uriunsplit(self.base), str(data))
        return File('file:///' + str(data))

    @twopaths
    def place(self, cache, path):
        mkdir('-p', path.dirname)
        if self.dirlike:
            rsync('-ai', str(self.data(cache)) + '/', str(path))
        else:
            cp(str(self.data(cache)), str(path))

    @onepath
    def run(self, cache, args=[]):
        if self.dirlike:
            raise Invalid('Arx can not run directory-like (ending with `/`) '
                          'S3 paths.')
        item = self.data(cache)
        chmod('a+rx', str(item))
        cmd = Command(str(item))
        cmd(*args)


class S3Tar(Tar, S3):
    """Links to tar archives available over S3.

    Note that these URLs may not end with a slash.

    These URLs have directory nature unless a fragment is passed, as described
    under :class:`~arx.sources.tar.Tar`.
    """

    @oneurl
    @schemes('tar+s3')
    def __init__(self, url):
        self.url = url
        if self.dirlike:
            raise Invalid('Arx can not treat directory-like (ending with `/`) '
                          'S3 paths like tarballs.')

    @onepath
    def cache(self, cache):
        as_file = super(S3Tar, self).cache(cache)
        return FileTar.resolve(as_file.resolved)

    def sign(self):
        return HTTPTar('tar+' + self.signed_get())


class S3Jar(Jar, S3):
    @oneurl
    @schemes('jar+s3')
    def __init__(self, url):
        self.url = url
        if self.url.fragment is not None:
            raise Invalid('Arx can not handle Jar S3 URLs with fragments.')
        if self.dirlike:
            raise Invalid('Arx can not treat directory-like (ending with `/`) '
                          'S3 paths like Jars.')

    def sign(self):
        return HTTPJar('jar+' + self.signed_get())


class Invalid(Err):
    pass
