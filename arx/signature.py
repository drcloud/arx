from functools import wraps


def signature(*types, **kwtypes):
    conversions = [(t if isinstance(t, tuple) else (t, t)) for t in types]
    kwconversions = {k: (t if isinstance(t, tuple) else (t, t))
                     for k, t in kwtypes.items()}

    def decorator(fn):
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            args = [(arg if isinstance(arg, t) else conv(arg))
                    for (t, conv), arg in zip(conversions, args)]
            kwargs = {k: (arg if isinstance(arg, t) else conv(arg))
                      for k, (t, conv), v
                      in ((k, kwconversions[k], v)
                          for k, v in kwargs.items())}
            return fn(self, *args, **kwargs)

        return wrapped

    return decorator
