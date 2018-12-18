import os
import time
import unittest

import pytest
from Jumpscale import j
from zerorobot.task.storage.base import TaskConflictError
from zerorobot.task.storage.file import TaskStorageFile
from zerorobot.task.task import Task
from zerorobot.task.task_list import TaskList, TaskNotFoundError


class _FakeService:

    def __init__(self):
        self.guid = "guid"
        self._path = j.sal.fs.getTmpDirPath()

    def install(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass


class TestTaskStorageFile(unittest.TestCase):

    def setUp(self):
        self.service = _FakeService()
        self.task_list = TaskList(self.service)
        self.storage = TaskStorageFile(self.task_list)
        self.task_list._done = self.storage

    def tearDown(self):
        j.sal.fs.removeDirTree(self.service._path)

    def _add_task(self):
        task = Task(self.service.install, None)
        self.storage.add(task)
        return task

    def test_init(self):
        assert self.storage._root is not None
        assert os.path.exists(self.storage._root)
        assert self.storage._root == os.path.join(self.service._path, 'tasks')
        assert self.storage._count == 0
        assert self.storage._count == self.storage.count()

    def test_task_path(self):
        task = Task(self.service.install, None)
        self.storage.add(task)
        assert self.storage._task_path(task) == os.path.join(self.storage._root, "%d_%s" % (self.storage._count, task.guid))
        assert os.path.exists(self.storage._task_path(task))

    def test_add(self):
        task = self._add_task()
        assert self.storage.count() == 1
        path = os.path.join(self.storage._root, "%d_%s" % (self.storage.count(), task.guid))
        assert os.path.exists(path)
        assert len(os.listdir(self.storage._root)) == 1

        for i in range(10):
            self._add_task()

        assert len(os.listdir(self.storage._root)) == 11
        assert self.storage.count() == 11

    def test_get(self):
        expected = self._add_task()

        actual = self.storage.get(expected.guid)
        assert compare_task(expected, actual)

        with pytest.raises(TaskNotFoundError):
            self.storage.get('no_exist')

        self.storage.add(expected)
        with pytest.raises(TaskConflictError):
            self.storage.get(expected.guid)

    def test_list(self):
        assert len(self.storage.list()) == 0
        assert len(self.storage.list()) == self.storage.count()

        tasks = {}
        for i in range(10):
            task = self._add_task()
            tasks[task.guid] = task

        assert len(self.storage.list()) == 10
        assert len(self.storage.list()) == self.storage.count()
        actuals = {task.guid: task for task in self.storage.list()}
        for guid, actual in actuals.items():
            expected = tasks[actual.guid]
            assert compare_task(expected, actual)

        before = int(time.time())
        time.sleep(1)
        after = int(time.time())
        tasks = []
        for i in range(10):
            tasks.append(self._add_task())

        assert len(self.storage.list()) == 20
        assert len(self.storage.list(from_timestap=after)) == 10
        assert len(self.storage.list(to_timestap=before)) == 10

    def test_drop(self):
        tasks = []
        for i in range(10):
            tasks.append(self._add_task())

        assert len(self.storage.list()) == 10
        assert 10 == self.storage.count()

        self.storage.drop()
        assert 0 == self.storage.count()


def compare_task(a, b):
    for attr in [
        'guid',
        'service',
        'action_name',
        '_args',
        '_priority',
        '_created',
    ]:
        return getattr(a, attr) == getattr(b, attr)

