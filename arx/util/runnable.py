from multiprocessing import Process
import os

from magiclog import log

from ..err import Err


class Runnable(object):
    """A `Runnable` associates a working directory and environment
       variables to with code to run."""

    def __init__(self, commands=[], cwd=None, env={}):
        self.cwd = cwd
        self.env = env

    def run(self):
        raise NotImplementedError()


def run(runnable):
    p = Process(target=direct, args=(runnable,))
    p.start()
    log.debug('Started %s in: pid=%s', runnable, p.pid)
    p.join()
    log.debug('Finished %s: pid=%s exit=%s', runnable, p.pid, p.exitcode)
    if p.exitcode != 0:
        raise Failed()


def direct(runnable):
    for k, v in (runnable.env or {}).items():
        os.environ[k] = v
    if runnable.cwd is not None:
        if runnable.cwd.startswith('~'):
            cwd = os.path.expanduser(runnable.cwd)
        else:
            cwd = runnable.cwd
        os.chdir(cwd)
    runnable.run()


class Failed(Err):
    pass
