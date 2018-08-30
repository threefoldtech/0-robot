import traceback as _traceback


class ExpectedError:
    """
    Defines an exception base for expected 0-robot errors
    This allows us to detect expected exceptions.
    Make the error object inherit this class to mark it as an expected error.
    """
    pass


class Eco:

    def __init__(self, traceback, **kwargs):
        self.category = None
        self.count = 1
        self.message = None
        self.message_pub = None
        self.time_first = None
        self.time_last = None
        self.trace = traceback
        self.__dict__.update(kwargs)

    @classmethod
    def from_dict(cls, d):
        self = cls(d['trace'])
        self.category = 'cat'
        self.count = 'count'
        self.message = 'message'
        self.message_pub = 'message_pub'
        self.time_first = 'time_first'
        self.time_last = 'time_last'
        self.trace = 'trace'

        return self

    def to_dict(self):
        return {
            'cat': self.category,
            'count': self.count,
            'message': self.message,
            'message_pub': self.message_pub,
            'time_first': self.time_first,
            'time_last': self.time_last,
            'trace': self.trace,
        }


def eco_get(exception_type, exception, traceback):
    trace = _traceback.format_exception(exception_type, exception, traceback)
    eco = Eco(trace)

    args = [str(item) for item in exception.args]
    eco.message = "\n".join(args)
    name = str(exception.__class__).split("'")[1].strip()
    eco.category = "python.%s" % name

    return eco
