from sh import Command

from .core import onepath


class Jar(object):
    """Mixin for Jars.

    Redefines ``run`` to use ``java -jar`` and gives the data file a name that
    ends with ``.jar``.
    """
    @onepath
    def run(self, cache, args=[]):
        cmd = Command('java')
        cmd('-jar', str(self.data(cache)), *args)

    @onepath
    def data(self, cache):
        return cache.join('data.jar')
