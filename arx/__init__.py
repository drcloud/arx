from collections import namedtuple

import six
from v2 import v2

from .bundle import Bundle, Code, Data
from .inner.schematics import interpreter_injector
from .sources import interpreter
from .sources.core import DiskLocal


__version__ = v2.from_pkg().from_git().from_default().version


class Arx(namedtuple('Arx', 'interpreter')):
    def Bundle(self, *args, **kwargs):
        """Generate a new bundle. Inputs, if passed, are used to initialize
           the bundle.
        """
        with interpreter_injector.using(self.interpreter):   # NB: Evil globals
            bundle = Bundle(*args, **kwargs)
            bundle.validate()
            return bundle

    def Source(self, *args, **kwargs):
        return self.interpreter(*args, **kwargs)

    def Code(self, *args, **kwargs):
        """Generate a new Code object, translating URLs and other sources
           according to this context's interpreter.
        """
        if len(args) > 0:
            if isinstance(args[0], six.string_types) and '://' not in args[0]:
                kwargs.update(cmd=args[0])
            else:
                kwargs.update(source=self.Source(args[0]))
            kwargs.update(args=args[1:])
            args = []
        code = Code(*args, **kwargs)
        code.validate()
        return code

    def Data(self, *args, **kwargs):
        """Generate a new Data object, translating URLs and other sources
           according to this context's interpreter.
        """
        if len(args) > 0:
            kwargs.update(source=self.Source(args[0]))
            args = args[1:]
        if len(args) > 0:
            kwargs.update(target=args[0])
            args = args[1:]
        data = Data(*args, **kwargs)
        data.validate()
        return data

    def local(self, source, under=None):
        cached = source.cache(under)
        assert isinstance(cached, DiskLocal)
        return self.Source(cached.externalize())

    def inline(self, source):
        raise NotImplementedError()


arx = Arx(interpreter.default)
