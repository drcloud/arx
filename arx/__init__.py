from collections import namedtuple

import six
from v2 import v2

from .bundle import Bundle, Code, Data
from .inner.schematics import interpreter_injector
from .sources import interpreter
from .sources.core import DiskLocal


__version__ = v2.from_pkg().from_git().from_default().version


class Arx(namedtuple('Arx', 'interpreter')):
    """An Arx API object encapsulates configuration for the convenience API.

    API configuration includes an interpreter (a callable) that translates
    strings and simple string dictionaries to URLs, as well as settings for
    temporary directory setup and task logging.
    """

    def Bundle(self, *args, **kwargs):
        """A convenience method for obtaining :class:`~arx.bundle.Bundle`\s
           which can be called with a variety of argument types.

        .. method::
            Bundle(code=[Code], data=[Data], cwd=str, label=str, env=dict)

            With keyword arguments. These keyword arguments can all be
            empty -- the default bundle has no additional environment, runs
            in a temporary directory and does not have a custom label.

        .. method:: Bundle(a: Code|Data, b: Code|Data, c: Code|Data, ...)

            With :class:`~arx.bundle.Code` and :class:`~arx.bundle.Data`
            objects as arguments, in any order.

        .. method:: Bundle(h: io.IOBase)

            With a handle -- an open file or :class:`StringIO` like object.
            The contents are read and passed through a YAML parser. The
            resulting dictionary object is passed to the dictionary form
            mentioned below.

        .. method:: Bundle({...}: dict)

            With a :class:`dict`, as is provided by parsing a JSON or YAML
            file. The arguments of the dict should mirror those of the
            keyword arguments form, above.

        Note that the keyword arguments ``cwd``, ``label`` and ``env`` from the
        first form can also be passed to any of the following forms.

        """
        with interpreter_injector.using(self.interpreter):   # NB: Evil globals
            bundle = Bundle(*args, **kwargs)
            bundle.validate()
            return bundle

    def Source(self, *args, **kwargs):
        return self.interpreter(*args, **kwargs)

    def Code(self, *args, **kwargs):
        """Convenience method for constructing :class:`~arx.bundle.Code`,
           which handles translation of strings and simple datatypes to
           :class:`~arx.sources.core.Source`\s.
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
        """Convenience method for constructing :class:`~arx.bundle.Data`,
           which handles translation of strings and simple datatypes to
           :class:`~arx.sources.core.Source`\s.
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
