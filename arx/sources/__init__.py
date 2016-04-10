from collections import Mapping
import re

from magiclog import log
import six
import uritools

from ..err import Err
from ..inner.uritools import uridisplay
from .core import DiskLocal, SignableURL, Source, SourceURL
from .http import HTTP, HTTPJar, HTTPTar
from .inline import InlineBinary, InlineJar, InlineTarGZ, InlineText
from .s3 import S3, S3Jar, S3Tar


class Interpreter(object):
    def __init__(self, uri_handlers=[], data_handlers=[]):
        self.uri_handlers = uri_handlers
        self.data_handlers = data_handlers

    def __call__(self, source):
        if isinstance(source, (Source, SourceURL, SignableURL, DiskLocal)):
            log.debug('Not reinterpreting source: %r', source)
            return source
        if isinstance(source, Mapping):
            log.debug('Treating as map: %s', source)
            if len(source) != 1:
                raise BadSourceFormat('Dictionary sources must be 1 element.')
            kind, data = list(source.items())[0]
            return Interpreter.apply_handlers(kind, data, self.data_handlers)
        if isinstance(source, six.string_types):
            source = uritools.urisplit(source)
        if isinstance(source, uritools.SplitResult):
            log.debug('Treating as URL: %s', uridisplay(source))
            kind = source.scheme
            return Interpreter.apply_handlers(kind, source, self.uri_handlers)
        raise BadSourceFormat('Please pass either a string or a dictionary.')

    @staticmethod
    def apply_handlers(kind, data, handlers):
        for pattern, handler in handlers:
            if isinstance(pattern, six.string_types):
                if kind != pattern:
                    continue
                return handler(data)
            if isinstance(pattern, _re_type):
                if not pattern.match(kind):
                    continue
                return handler(data)
            raise UnhandledPatternType('Type %s cannot be used as a pattern.' %
                                       type(pattern).__name__)


interpret = Interpreter(
    uri_handlers=[
        (re.compile('https?'), HTTP),
        (re.compile('jar[+]https?'), HTTPJar),
        (re.compile('tar[+]https?'), HTTPTar),
        (re.compile('s3'), S3),
        (re.compile('jar[+]s3'), S3Jar),
        (re.compile('tar[+]s3'), S3Tar)
    ],
    data_handlers=[
        ('text', InlineText),
        ('data', InlineBinary),
        ('jar', InlineJar),
        ('tgz', InlineTarGZ),
        ('base64', InlineBinary.base64),
        ('jar64', InlineJar.base64),
        ('tgz64', InlineTarGZ.base64)
    ]
)


class UnhandledPatternType(Err):
    pass


class UnknownSourceFormat(Err):
    pass


class BadSourceFormat(Err):
    pass


_re_type = type(re.compile(''))
