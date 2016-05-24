from __future__ import absolute_import
from collections import Sequence
from contextlib import contextmanager
import threading

import schematics.models
from schematics.types import BaseType
import six

from ..sources import interpreter


class Model(schematics.models.Model):
    def __init__(self, *args, **kwargs):
        for arg in args:
            kwargs.update(**arg)
        super(Model, self).__init__(kwargs)

    def __repr__(self):
        fields = ((k, self._data[k]) for k in self._fields.keys())
        notnull = ((k, d) for k, d in fields if nonempty(d))
        return '%s(%s)' % (type(self).__name__,
                           ', '.join('%s=%r' % (k, d) for k, d in notnull))

    def to_primitive(self):
        return simplify(super(Model, self).to_primitive())

    class Options:
        serialize_when_none = False


def simplify(item):
    """Trim away null and empty fields of a model when serializing.
    """
    return dict((k, v) for k, v in item.items() if nonempty(v))


def nonempty(x):
    return x is not None and not (isinstance(x, Sequence) and not
                                  isinstance(x, six.string_types) and
                                  len(x) == 0)


class SourceType(BaseType):
    def to_native(self, value, context=None):
        val = interpreter_injector(value)
        if val is None:
            raise ValueError('Invalid complex source.')
        return val

    def to_primitive(self, value, context=None):
        return value.externalize()


# We lack an easy way to parameterize a source type with the containing Arx
# object's interpreter; so instead we allow the interpreter to be updated
# with a context manager.

class InterpreterInjector(object):
    def __init__(self):
        self.lock = threading.RLock()
        self._interpreter = interpreter.default

    @property
    def interpreter(self):
        with self.lock:
            return self._interpreter

    @contextmanager
    def using(self, interpreter):
        with self.lock:
            old = self._interpreter
            self._interpreter = interpreter
            yield
            self._interpreter = old

    def __call__(self, *args, **kwargs):
        with self.lock:
            assert self._interpreter is not None
            return self._interpreter(*args, **kwargs)


interpreter_injector = InterpreterInjector()
