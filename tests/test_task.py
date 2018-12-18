import time
import unittest

import gevent
from zerorobot.task.task import (TASK_STATE_ERROR, TASK_STATE_NEW,
                                 TASK_STATE_OK, TASK_STATE_RUNNING, Task)
from zerorobot.template.decorator import timeout


def noop():
    return "foo"


@timeout(10)
def with_decorator():
    return "foo"


@timeout(10)
def with_decorator_error():
    raise RuntimeError('oopsy daisy')


def wait():
    time.sleep(10)
    return "done"


class TestTask(unittest.TestCase):

    def test_create_task(self):
        t = Task(noop, {})
        assert t.guid is not None
        assert t.state == TASK_STATE_NEW
        assert t._func == noop
        assert t.action_name == 'noop'
        assert t.created is not None and t.created < time.time()

    def test_execute_task(self):
        for func in [noop, with_decorator]:
            t = Task(noop, {})
            t.execute()
            assert t.duration > 0
            assert t.eco is None
            assert t.result == 'foo'
            assert t.state == TASK_STATE_OK

    def test_execute_error(self):
        t = Task(with_decorator_error, {})
        t.execute()
        assert t.state == TASK_STATE_ERROR
        assert t.eco is not None

        # task.wait should not raise is state is error but die is False
        t.wait(die=False)

        with self.assertRaises(RuntimeError, msg='task.wait should raise if state is error and die is True'):
            t.wait(die=True)

    def test_cancel_timeout(self):
        t = Task(wait, {})
        g = gevent.spawn(t.execute)

        with self.assertRaises(TimeoutError):
            t.wait(timeout=3)

        g.join()  # wait for the greenlet executing the task finishes

        assert t.state == TASK_STATE_ERROR
        assert t.duration > 0
        assert t.result is None
        assert t.created > 0
        assert t.eco is not None

    def test_cancel(self):
        t = Task(wait, {})
        g = gevent.spawn(t.execute)

        time.sleep(2)
        t._cancel()
        g.join()  # wait for the greenlet executing the task finishes

        assert t.state == TASK_STATE_ERROR
        assert t.duration > 0
        assert t.result is None
        assert t.created > 0
        assert t.eco is not None
