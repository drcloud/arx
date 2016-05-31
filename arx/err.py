class Err(Exception):
    """Base class for custom exceptions in this package."""
    def __init__(self, *args, **kwargs):
        if 'cause' in kwargs:
            self.cause = kwargs['cause']
            del kwargs['cause']
        else:
            self.cause = None
        super(Err, self).__init__(*args, **kwargs)
