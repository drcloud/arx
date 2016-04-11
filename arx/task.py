from collections import Mapping, Sequence
import os
import sys

from magiclog import log
from schematics.exceptions import ConversionError
from schematics.types import BaseType, StringType
from schematics.types.compound import DictType, ListType
from schematics.models import Model
import sh
import six

from .sources import interpret
from .util.runnable import run, Runnable
from .util.tmp import tmpdir


class SourceType(BaseType):
    def to_native(self, value, context=None):
        val = interpret(value)
        if val is None:
            raise ValueError('Invalid complex source.')
        return val

    def to_primitive(self, value, context=None):
        return value.externalize()


class RunnableModel(Model, Runnable):
    cwd = StringType()
    env = DictType(StringType())

    class Options:
            serialize_when_none = False


class Code(RunnableModel):
    source = SourceType()
    cmd = ListType(StringType())
    args = ListType(StringType())

    def run(self):
        if self.source is not None:
            with tmpdir() as cache:
                log.debug('Running: %s', self.source)
                self.source.cache(cache)
                self.source.run(cache, (self.args or []))
        else:
            cmd = sh.Command(self.cmd[0])
            log.debug('Running: %s', cmd)
            cmd(*(self.cmd[1:] + (self.args or [])),
                _out=sys.stdout, _err=sys.stderr)


class Data(RunnableModel):
    source = SourceType(required=True)
    target = StringType()

    def run(self):
        log.debug('Unpacking: %s', self.source)
        with tmpdir() as cache:
            target = self.target or os.getcwd()
            self.source.cache(cache)
            self.source.place(cache, target)


class IdiomaticCodeModelType(BaseType):
    def to_native(self, value, context=None):
        if isinstance(value, six.string_types):
            value = [value]
        if isinstance(value, Sequence):
            if '://' in value[0]:
                value = dict(source=interpret(value[0]), args=value[1:])
            else:
                value = dict(cmd=value[0], args=value[1:])
        if isinstance(value, Mapping):
            if 'cmd' in value:
                if isinstance(value['cmd'], six.string_types):
                    value['cmd'] = [value['cmd']]
        if 'cmd' in value and 'source' in value:
            raise ConversionError('A Code has either: cmd= or source=')
        if 'cmd' not in value and 'source' not in value:
            raise ConversionError('A Code has one of: cmd= or source=')
        return Code(value)

    def to_primitive(self, value, context=None):
        prim = value.to_primitive()
        if set(prim.keys()) == set(['source']):
            return prim['source']                          # Simplify to string
        if set(prim.keys()) == set(['cmd']) and len(prim['cmd']) == 1:
            return prim['cmd'][0]                          # Simplify to string
        if set(prim.keys()) < set(['source', 'cmd', 'args']):
            cmd = [prim['source']] if 'source' in prim else prim['cmd']
            return cmd + prim['args']                       # Simplify to array
        return prim


class IdiomaticDataModelType(BaseType):
    def to_native(self, value, context=None):
        if isinstance(value, six.string_types):
            value = dict(source=value)
        if not isinstance(value, Mapping):
            raise ConversionError('A Data must be either a single string or a '
                                  'map.')
        if 'source' not in value:
            if len(value) != 1:
                raise ConversionError('A simple Data map must be a map of one '
                                      'element map.')
            source, target = list(value.items())[0]
            value = dict(source=source, target=target)
        return Data(value)

    def to_primitive(self, value, context=None):
        prim = value.to_primitive()
        if isinstance(prim['source'], six.string_types):
            if set(prim.keys()) == set(['source']):
                return prim['source']                      # Simplify to string
            if set(prim.keys()) == set(['source', 'target']):
                return {prim['source']: prim['target']}   # Simplify to KV pair
        return prim


class Task(RunnableModel):
    code = ListType(IdiomaticCodeModelType())
    data = ListType(IdiomaticDataModelType())

    def run(self):
        for data in self.data:
            run(data)
        for code in self.code:
            run(code)
