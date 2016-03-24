import boto3
from sh import Command, chmod, cp, mkdir, rsync
import uritools

from ..err import Err
from .http import HTTP, HTTPTar, HTTPJar
from .jar import Jar
from ..decorators import schemes
from . import onepath, oneurl, SourceURL, twopaths
from .tar import Tar


class S3(SourceURL):
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
        # Allows subclasses to inherit this implementation by throwing away the
        # prefix.
        scheme = self.self.url.scheme.split('+')[-1]
        simplified_url = self.url._replace(scheme=scheme, fragment=None,
                                           authority=self.url.host)
        cmd = Command('aws')
        sub = 'sync' if self.dirlike else 'cp'
        cmd('s3', sub, uritools.uriunsplit(simplified_url),
            str(self.data(cache)))

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

    @onepath
    def data(self, cache):
        return cache.join('data')


class S3Tar(Tar, S3):
    @oneurl
    @schemes('tar+s3')
    def __init__(self, url):
        self.url = url
        if self.dirlike:
            raise Invalid('Arx can not treat directory-like (ending with `/`) '
                          'S3 paths like tarballs.')

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
