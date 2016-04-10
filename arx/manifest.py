from collections import Mapping, Sequence

from schematics.exceptions import ConversionError
from schematics.types import BaseType, StringType
from schematics.types.compound import DictType, ListType
from schematics.models import Model
import six

from .sources import interpret


class SourceType(BaseType):
    def to_native(self, value, context=None):
        val = interpret(value)
        if val is None:
            raise ValueError('Invalid complex source.')
        return val

    def to_primitive(self, value, context=None):
        return value.externalize()


class Code(Model):
    source = SourceType()
    cmd = ListType(StringType())
    args = ListType(StringType())
    cwd = StringType()
    env = DictType(StringType())
    label = StringType()

    class Options:
            serialize_when_none = False


class Data(Model):
    source = SourceType(required=True)
    target = StringType()
    label = StringType()
    env = DictType(StringType())

    class Options:
            serialize_when_none = False


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
        if all([set(prim.keys()) < set(['source', 'cmd']),
                len(prim.get('cmd', [])) <= 1]):           # Simplify to string
            return prim.get('source') or prim.get('cmd')[0]
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


class Task(Model):
    code = ListType(IdiomaticCodeModelType())
    data = ListType(IdiomaticDataModelType())
    cwd = StringType()
    env = DictType(StringType())
    label = StringType()

    class Options:
            serialize_when_none = False
