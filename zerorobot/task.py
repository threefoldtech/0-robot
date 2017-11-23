import gevent
from gevent.queue import Queue
import time

from js9 import j

# Task state constant
TASK_STATE_NEW = "new"
TASK_STATE_RUNNING = "running"
TASK_STATE_OK = "ok"
TASK_STATE_ERROR = "error"


class Task:

    def __init__(self, action, args, resp_q=None):
        """
        @param action: is the method that this task need to execute
        @param args: argument to pass to the action when executing
        @param resp_q: is the response queue on which the result of the action need to be put
        """
        self.guid = j.data.idgenerator.generateGUID()
        self._action = action
        self._resp_q = resp_q
        self._args = args
        self._state = TASK_STATE_NEW

    def execute(self):
        if self._action is None:
            return

        self._state = TASK_STATE_RUNNING
        # TODO: handle retries, exception, logging,...
        result = None
        try:
            result = self._action(*self._args)
            self._state = TASK_STATE_OK
        except Exception as err:
            self._state = TASK_STATE_ERROR
            raise err
        finally:
            if result and self._resp_q:
                self._resp_q.put(result)

    @property
    def state(self):
        return self._state


class TaskList:
    """
    Task list if a FIFO queue of tasks
    """

    def __init__(self):
        self._queue = Queue()

    def get(self):
        """
        pop out a task from the task list
        this call is blocking when the task list is empty
        """
        return self._queue.get()

    def put(self, task):
        """
        append task to the task list
        """
        if not isinstance(task, Task):
            raise ValueError("task should be an instance of the Task class not %s" % type(task))
        self._queue.put(task)

    def empty(self):
        """
        return True is the task list is empty, False otherwise
        """
        return self._queue.empty()
