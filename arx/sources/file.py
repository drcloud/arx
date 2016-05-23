from ..decorators import schemes
from ..err import Err
from .jar import Jar
from .core import DiskLocal, onepath, oneurl, SourceURL, twopaths
from .tar import Tar


class File(DiskLocal, SourceURL):
    @oneurl
    @schemes('file')
    def __init__(self, url):
        self.url = url
        if url.fragment is not None:
            raise Invalid('Arx can not work with plain file URLs that have '
                          'fragments.')

    @onepath
    def cache(self, cache):
        raise NotImplementedError()

    @twopaths
    def place(self, cache, path):
        raise NotImplementedError()

    @onepath
    def run(self, cache, args=[]):
        raise NotImplementedError()

    @onepath
    def datapath(self, cache):
        return cache.join('filedata')


class FileTar(Tar, File):
    @oneurl
    @schemes('tar+file')
    def __init__(self, url):
        self.url = url


class FileJar(Jar, File):
    @oneurl
    @schemes('jar+file')
    def __init__(self, url):
        self.url = url
        if url.fragment is not None:
            raise Invalid('Arx can not handle Jar file URLs with fragments.')


class Invalid(Err):
    pass
