from functools import wraps

from err import Err


def schemes(*schemes):
    """URL scheme validation.

    This validator when supplied with a list of schemes ensures that first
    argument of the decorated function is a URL with one of those schemes.
    """

    msg = 'The accepted schemes for %s (which are: %s) do not include: %s'

    def decorator(fn):
        @wraps(fn)
        def wrapped(self, url, *args, **kwargs):
            if url.scheme not in schemes:
                raise InvalidScheme(msg % (type(self).__name__,
                                           ', '.join(schemes),
                                           str(url.scheme)))
            return fn(self, url, *args, **kwargs)

        return wrapped

    return decorator


class InvalidScheme(Err):
    pass
