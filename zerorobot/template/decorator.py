from functools import wraps
import signal
import time


def retry(exceptions, tries=4, delay=3, backoff=2, logger=None):
    """
    Retry calling the decorated function using an exponential backoff.

    Args:
        exceptions: The exception to check. may be a tuple of
            exceptions to check.
        tries: Number of times to try (not retry) before giving up.
        delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier (e.g. value of 2 will double the delay
            each retry).
        logger: Logger to use. If None, print.
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    msg = '{}, Retrying in {} seconds...'.format(e, mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


def timeout(seconds, error_message='Function call timed out'):
    """
    Raise a Timeout error if the wrapped function takes more time then seconds to execute.

    Args:
        seconds: timeout time in seconds
        error_message: message to pass to the TimeoutError exception raised
    """
    def deco_timout(f):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @wraps(f)
        def f_timeout(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = f(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return f_timeout

    return deco_timout
