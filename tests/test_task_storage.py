import os
import time
import unittest

import pytest
from Jumpscale import j
from zerorobot.task.storage.base import TaskConflictError
from zerorobot.task.storage.file import TaskStorageFile
from zerorobot.task.storage.sqlite import TaskStorageSqlite
from zerorobot.task.task import Task
from zerorobot.task.task_list import TaskList, TaskNotFoundError


class _FakeService:

    def __init__(self):
        self.guid = j.data.idgenerator.generateGUID()
        self._path = j.sal.fs.getTmpDirPath()

    def install(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass


class TestTaskStorageBase(unittest.TestCase):

    def __init__(self, methodName):
        super().__init__(methodName)
        self.storage_class = None

    def setUp(self):
        def load(storage_class):
            service = _FakeService()
            task_list = TaskList(service)
            storage = storage_class(task_list)
            task_list._done = storage
            return storage

        self.storages = map(load, [TaskStorageSqlite, TaskStorageFile])

    def tearDown(self):
        map(lambda storage: storage.drop(), self.storages)

    def test_init(self):
        def test(storage):
            assert storage.count() == 0
            assert storage.count() == storage.count()
            assert storage.count() == len(storage.list())
        list(map(test, self.storages))

    def test_add(self):
        def test(storage):
            task = add_task(storage)
            assert storage.count() == 1

            for i in range(10):
                add_task(storage)

            assert storage.count() == 11

        list(map(test, self.storages))

    def test_get(self):
        def test(storage):
            expected = add_task(storage)

            actual = storage.get(expected.guid)
            assert compare_task(expected, actual)

            with pytest.raises(TaskNotFoundError):
                storage.get('no_exist')

            with pytest.raises(TaskConflictError):
                storage.add(expected)
                storage.get(expected.guid)

        list(map(test, self.storages))

    def test_list(self):
        def test(storage):
            assert len(storage.list()) == 0
            assert len(storage.list()) == storage.count()

            tasks = {}
            for i in range(10):
                task = add_task(storage)
                tasks[task.guid] = task

            assert len(storage.list()) == 10
            assert len(storage.list()) == storage.count()
            actuals = {task.guid: task for task in storage.list()}
            for guid, actual in actuals.items():
                expected = tasks[actual.guid]
                assert compare_task(expected, actual)

            before = int(time.time())
            time.sleep(1)
            after = int(time.time())
            tasks = []
            for i in range(10):
                tasks.append(add_task(storage))

            assert len(storage.list()) == 20
            assert len(storage.list(from_timestap=after)) == 10
            assert len(storage.list(to_timestap=before)) == 10

        list(map(test, self.storages))

    def test_drop(self):
        def test(storage):
            tasks = []
            for i in range(10):
                tasks.append(add_task(storage))

            assert len(storage.list()) == 10
            assert 10 == storage.count()

            storage.drop()
            assert 0 == storage.count()

        list(map(test, self.storages))


def add_task(storage):
    service = _FakeService()
    task = Task(service.install, None)
    storage.add(task)
    return task


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

