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
        self.category = ''
        self.count = 1
        self.message = ''
        self.message_pub = ''
        self.time_first = 0
        self.time_last = 0
        self.trace = traceback
        self.__dict__.update(kwargs)

    @classmethod
    def from_dict(cls, d):
        self = cls(d.get('trace'))
        self.category = d.get('cat')
        self.count = d.get('count')
        self.message = d.get('message')
        self.message_pub = d.get('message_pub')
        self.time_first = d.get('time_first')
        self.time_last = d.get('time_last')
        self.trace = d.get('trace')

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
    eco = Eco('\n'.join(trace))

    args = [str(item) for item in exception.args]
    eco.message = "\n".join(args)
    name = str(exception.__class__).split("'")[1].strip()
    eco.category = "python.%s" % name

    return eco
