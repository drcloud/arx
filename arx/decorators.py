from functools import wraps

from .err import Err


def signature(*types, **kwtypes):
    """Type annotations and conversions for methods.

    Ignores first parameter.
    """
    conversions = [(t if isinstance(t, tuple) else (t, t)) for t in types]
    kwconversions = {k: (t if isinstance(t, tuple) else (t, t))
                     for k, t in kwtypes.items()}

    def decorator(fn):
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            args = [(arg if isinstance(arg, t) else conv(arg))
                    for (t, conv), arg in zip(conversions, args)]
            kwargs = {k: (v if isinstance(v, t) else conv(v))
                      for k, (t, conv), v
                      in ((k, kwconversions[k], v)
                          for k, v in kwargs.items())}
            return fn(self, *args, **kwargs)

        return wrapped

    return decorator


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
