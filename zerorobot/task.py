"""
task module holds the logic regarding TaskList and Task classes.

These two classes are used by the services to managed the requested actions
"""

import json
import os
import sys
import time

import gevent
from gevent.lock import Semaphore
from gevent.queue import Queue
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
        self.created = int(time.time())

        # used when action raises an exception
        self.eco = None

        self._state = TASK_STATE_NEW
        self._state_lock = Semaphore()

    def execute(self):

        self.state = TASK_STATE_RUNNING
        # TODO: handle logging,...
        result = None

        try:
            if self._args is not None:
                result = eval('self.service.%s(**self._args)' % self.action_name)
            else:
                result = eval('self.service.%s()' % self.action_name)
            self.state = TASK_STATE_OK
        except Exception as err:
            self.state = TASK_STATE_ERROR
            # capture stacktrace and exception
            _, _, exc_traceback = sys.exc_info()
            self.eco = j.core.errorhandler.parsePythonExceptionObject(err, tb=exc_traceback)
            self.eco.printTraceback()

        finally:
            if result and self._resp_q:
                self._resp_q.put(result)
        return result

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

    def wait(self, timeout):
        """
        wait blocks until the task has been executed or after timout seconds
        """
        end = time.time() + timeout
        while self.state in ('new', 'running') and time.time() < end:
            gevent.sleep(1)


class TaskList:
    """
    Task list if a FIFO queue of tasks
    """

    def __init__(self):
        self._queue = Queue()
        self.running = None
        # done keeps the tasks that have been extracted from the queue
        # so we can inspect them later
        # TODO: done tasks should be kept on disk, not in memory
        self._done = []

    def get(self):
        """
        pop out a task from the task list
        this call is blocking when the task list is empty
        """
        task = self._queue.get()
        self._done.append(task)
        return task

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

    def list_tasks(self, all=False):
        """
        @param all: if True, also return the task that have been executed
                    if False only return the task waiting in the task list
        returns all the task that are currently in the task list
        """
        tasks = list(self._queue.queue)
        if all:
            tasks.extend(self._done)
        elif len(self._done) > 1 and self._done[-1].state == TASK_STATE_RUNNING:
            # also return the current running
            # task as part of the task list
            tasks.insert(0, self._done[-1])
        return tasks

    def get_task_by_guid(self, guid):
        """
        return a task from the list by it's guid
        """
        # FIXME: this is really inefficient
        def find_task(guid, l):
            for task in l:
                if task.guid == guid:
                    return task

        task = find_task(guid, self._queue.queue)
        if task:
            return task
        task = find_task(guid, self._done)
        if task:
            return task
        raise KeyError("no task with guid %s found" % guid)

    def save(self, path):
        """
        serialize the task list to disk
        @param path: file path where to serialize the task list
        """
        def serialize_task(task):
            return {
                "guid": task.guid,
                # "service": = task.service.name,
                "action_name": task.action_name,
                # "_resp_q": = resp_q TODO: figure out what to do with the resp_q
                "args": task._args,
                "state": task.state,
                "eco": json.loads(task.eco.toJson()) if task.eco else None,
            }
        # FIXME: stream into file instead, this can consume a lot
        # of memory in case lots of tasks
        output = []
        for task in self.list_tasks(all=True):
            output.append(serialize_task(task))
        j.data.serializer.yaml.dump(path, output)

    def load(self, path, service):
        """
        load a task list that have been serialized with save method
        @param path: file path where the task list is serialized
        @param service: the service object to which this task list belongs
        """
        def instanciate_task(task):
            t = Task(service, task['action_name'], task['args'], resp_q=None)
            if task['state'] in [TASK_STATE_RUNNING, TASK_STATE_NEW]:
                t.state = TASK_STATE_NEW
            else:
                t.state = task['state']
            t.guid = task['guid']
            if task['eco']:
                t.eco = j.core.errorhandler.getErrorConditionObject(ddict=task['eco'])
            return t

        if not os.path.exists(path):
            return

        data = j.data.serializer.yaml.load(path)
        for task in data:
            if task['state'] in [TASK_STATE_NEW, TASK_STATE_RUNNING]:
                self.put(instanciate_task(task))
            elif task['state'] in [TASK_STATE_OK, TASK_STATE_ERROR]:
                self._done.append(instanciate_task(task))
            else:
                # None supported state, just skip it
                continue
