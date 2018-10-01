from gevent import lock


class _ConfigLock:

    def __init__(self):
        self._lock = lock.BoundedSemaphore()

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, ttype, value, tb):
        self._lock.release()


config_lock = _ConfigLock()
