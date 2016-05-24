from collections import namedtuple
import pkg_resources

import six

from .bundle import Bundle, Code, Data
from .inner.schematics import interpreter_injector
from .sources import interpreter
from .sources.core import DiskLocal


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


def version():
    try:
        return pkg_resources.get_distribution(__package__).version
    except:
        pass
    try:
        return pkg_resources.resource_string(__package__, 'VERSION').strip()
    except:
        pass
    return '19991231'


__version__ = version()
