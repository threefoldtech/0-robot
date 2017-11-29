import gevent
from gevent.queue import Queue
from gevent.lock import Semaphore
import time

from js9 import j

# Task state constant
TASK_STATE_NEW = "new"
TASK_STATE_RUNNING = "running"
TASK_STATE_OK = "ok"
TASK_STATE_ERROR = "error"


class Task:

    def __init__(self, service, action_name, args, resp_q=None):
        """
        @param service: is the service object that own the action to be executed
        @param action_name: is the method name of the action that this task need to execute
        @param args: argument to pass to the action when executing
        @param resp_q: is the response queue on which the result of the action need to be put
        """
        self.guid = j.data.idgenerator.generateGUID()
        self.service = service
        self.action_name = action_name
        self._resp_q = resp_q
        self._args = args

        self._state = TASK_STATE_NEW
        self._state_lock = Semaphore()

    def execute(self):
        # if self._action is None:
        #     return

        self.state = TASK_STATE_RUNNING
        # TODO: handle retries, exception, logging,...
        result = None

        try:
            if self._args is not None:
                result = eval('self.service.%s(**self._args)' % self.action_name)
            else:
                result = eval('self.service.%s()' % self.action_name)
            self.state = TASK_STATE_OK
        except Exception as err:
            self.state = TASK_STATE_ERROR
            raise err
        finally:
            if result and self._resp_q:
                self._resp_q.put(result)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        try:
            self._state_lock.acquire()
            self._state = value
        finally:
            self._state_lock.release()


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

    def list_tasks(self):
        """
        returns all the task that are currently in the task list
        """
        if self.empty():
            return []
        return list(self._queue.queue)

    def get_task_by_guid(self, guid):
        """
        return a task from the list by it's guid
        """
        for task in self._queue.queue:
            if task.guid == guid:
                return task
        raise KeyError("no task with guid %s found" % guid)
