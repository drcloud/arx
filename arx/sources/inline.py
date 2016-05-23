from base64 import b64decode, b64encode
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
        body = cache.join('data')
        with open(body, 'w') as h:
            h.write(self.data)


class InlineText(Inline):
    @signature(str)
    def __init__(self, text):
        if not stringsafe(text):
            raise ValueError('Please use InlineBinary for non-ASCII text.')
        self.text = text

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

    @property
    def data(self):
        return six.b(self.text.strip() + '\n')

    def externalize(self):
        return dict(text=self.text)

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

    def externalize(self):
        lines = break_up_base64(b64encode(self.data))
        para = '\n'.join(b.decode() for b in lines)
        return dict(base64=para)

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

    def externalize(self):
        para = super(InlineTarGZ, self).externalize()['base64']
        return dict(tgz64=para)


class InlineJar(InlineBinary):
    @onepath
    def run(self, cache, args=[]):
        jar = cache.join('data.jar')
        self.place(cache, jar)
        cmd = Command('java')
        cmd('-jar', str(jar), *args)

    def externalize(self):
        para = super(InlineJar, self).externalize()['base64']
        return dict(jar64=para)


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


def break_up_base64(data, n=64):
    while len(data) > 0:
        yield data[:n]
        data = data[n:]


def stringsafe(data):
    text_code_points = (set([0x07, 0x08, 0x09, 0x0a, 0x0c, 0x0d, 0x1b]) |
                        set(range(0x20, 0x100)) - set([0x7f]))
    return len(data.translate(None, bytearray(text_code_points))) == 0
