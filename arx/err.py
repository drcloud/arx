class Err(Exception):
    """Base class for this package's exceptions."""
    def __init__(self, *args, **kwargs):
        if 'cause' in kwargs:
            self.cause = kwargs['cause']
            del kwargs['cause']
        else:
            self.underlying = None
        super(Err, self).__init__(*args, **kwargs)
