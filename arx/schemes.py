from functools import wraps

from err import Err


def schemes(*schemes):
    msg = 'The accepted schemes for %s (which are: %s) do not include: %s'

    def decorator(fn):
        @wraps(fn)
        def wrapped(self, url, *args, **kwargs):
            if url.scheme not in schemes:
                raise InvalidScheme(msg % (fn.im_class.__name__,
                                           ' '.join(schemes),
                                           str(url.scheme)))
            return fn(self, url, *args, **kwargs)

        return wrapped

    return decorator


class InvalidScheme(Err):
    pass
