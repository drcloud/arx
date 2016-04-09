from base64 import b64decode
from collections import Container, Mapping, OrderedDict, Sequence
import math

from sh import chmod, Command, mkdir, tar
import six

from ..decorators import signature
from ..err import Err
from .core import onepath, Source, twopaths


class Inline(Source):
    @onepath
    def cache(self, cache):
        """Caching for inline sources is a no-op."""
        pass


class InlineText(Inline):
    @signature(str)
    def __init__(self, text):
        self.text = text

    @twopaths
    def place(self, cache, path):
        mkdir('-p', path.dirname)
        with open(str(path), 'w') as h:
            h.write(self.text.strip() + '\n')

    @onepath
    def run(self, cache, args=[]):
        f = cache.join('data')
        self.place(cache, f)
        chmod('a+rx', str(f))
        cmd = Command(str(f))
        cmd(*args)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, clip(self.text[:20]))


class InlineBinary(Inline):
    @signature(bytes)
    def __init__(self, data):
        self.data = data

    @classmethod
    def base64(cls, text):
        return cls(b64decode(text))

    @twopaths
    def place(self, cache, path):
        mkdir('-p', path.dirname)
        with open(str(path), 'w') as h:
            h.write(self.data)

    @onepath
    def run(self, cache, args=[]):
        f = cache.join('data')
        self.place(cache, f)
        chmod('a+rx', str(f))
        cmd = Command(str(f))
        cmd(*args)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__,
                           clip(self.data[:20], ellipsis=six.b('...')))


class InlineTarGZ(InlineBinary):
    @onepath
    def run(self, cache, args=[]):
        raise NoExecutingInlineTars()

    @twopaths
    def place(self, cache, path):
        mkdir('-p', path)
        tar('-xz', '-C', str(path), _in=self.data)
        with open(str(path), 'w') as h:
            h.write(self.data)


class InlineJar(InlineBinary):
    @onepath
    def run(self, cache, args=[]):
        jar = cache.join('data.jar')
        self.place(cache, jar)
        cmd = Command('java')
        cmd('-jar', str(jar), *args)


class InlineCollection(Inline):
    @signature((Container, OrderedDict))
    def __init__(self, collection):
        self.collection = collection

    @twopaths
    def place(self, _cache, path):
        InlineCollection.unpack_collection(path, self.collection)

    @onepath
    def run(self, _cache, _args=[]):
        raise NoExecutingCollections('Collections can not be executed.')

    @staticmethod
    @onepath
    def unpack_pairs(under, pairs):
        for path, data in pairs:
            full = under.join(path)
            if isinstance(data, Container):
                InlineCollection.unpack_collection(full, data)
            else:
                mkdir('-p', full.dirname)
                # TODO: rm -rf, check links, &c
                with open(str(full), 'w') as h:
                    if isinstance(data, bytes):
                        h.write(bytes)
                    if hasattr(data, 'read'):
                        h.write(data.read())
                    h.write(str(data).strip() + '\n')

    @staticmethod
    def unpack_collection(under, collection):
        pairs = None
        if isinstance(Mapping, collection):
            pairs = collection.items()
        if isinstance(Sequence, collection):
            fmt = '%0' + math.ceil(math.log(len(collection), 10)) + 's'
            pairs = ((fmt % i, data) for i, data in enumerate(collection))
        if pairs is None:
            raise UnhandledCollection('Collection type %s is not handled.',
                                      type(collection).__name__)
        InlineCollection.unpack_pairs(under, pairs)


class UnhandledCollection(Err):
    pass


class NoExecutingCollections(Err):
    pass


class NoExecutingInlineTars(Err):
    pass


def clip(something, ellipsis='...', n=20):
    return something if len(something) <= n else something[:n] + ellipsis
