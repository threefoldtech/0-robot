import unittest

from zerorobot.task import PRIORITY_NORMAL, PRIORITY_SYSTEM, Task, TaskList


class FakeService:

    def __init__(self, name):
        self.name = name

    def foo(self):
        pass

    def bar(self):
        pass


class TestTaskList(unittest.TestCase):

    def _get_tasks(self, nr):
        tasks = []
        for i in range(nr):
            s = FakeService("s%d" % i)
            t = Task(s.foo, {})
            tasks.append(t)
        return tasks

    def test_create_list(self):
        tl = TaskList()
        self.assertIsNotNone(tl._queue)
        self.assertEqual(tl._done, [])
        self.assertTrue(tl.empty())

    def test_put(self):
        tl = TaskList()
        with self.assertRaises(ValueError, msg="should raise when trying to put an object that is not a Task"):
            tl.put('string')

        self.assertTrue(tl.empty())
        srv = FakeService('s1')
        t = Task(srv.foo, {})
        tl.put(t)
        self.assertFalse(tl.empty())
        t2 = tl.get()
        self.assertEqual(t, t2, "task extracted from the list should be the same as the task added")
        self.assertEqual(tl._done[0], t, "task extracted from the list should be kept in the _done list")

    def test_get(self):
        tl = TaskList()

        tasks = self._get_tasks(3)
        for t in tasks:
            tl.put(t)

        returned_tasks = []
        while not tl.empty():
            returned_tasks.append(tl.get())
        self.assertEqual(returned_tasks, tasks)

    def test_get_by_guid(self):
        tl = TaskList()

        tasks = self._get_tasks(3)
        for t in tasks:
            tl.put(t)

        t1 = tasks[0]

        task = tl.get_task_by_guid(t1.guid)
        self.assertEqual(task, t1)
        with self.assertRaises(KeyError):
            tl.get_task_by_guid('1111')

    def test_list(self):
        tl = TaskList()

        tasks = self._get_tasks(2)
        for t in tasks:
            tl.put(t)

        returned_tasks = tl.list_tasks()
        self.assertEqual(returned_tasks, tasks, "listing of tasks should return all enqueued tasks")

        _ = tl.get()
        returned_tasks = tl.list_tasks()
        self.assertEqual(returned_tasks, tasks[1:], "listing of tasks should return all enqueued tasks")

        all_tasks = tl.list_tasks(all=True)
        self.assertEqual(all_tasks, list(reversed(tasks)), "listing of all tasks should return all enqueued tasks and all done tasks")

    def test_priority(self):
        tl = TaskList()

        s1 = FakeService("s1")
        s2 = FakeService("s2")
        s3 = FakeService("s3")

        t1 = Task(s1.foo, {})
        t2 = Task(s1.foo, {})
        t3 = Task(s1.foo, {})

        tl.put(t1, priority=PRIORITY_NORMAL)
        tl.put(t2, priority=PRIORITY_NORMAL)
        tl.put(t3, priority=PRIORITY_SYSTEM)

        tasks = []
        while not tl.empty():
            tasks.append(tl.get())

        self.assertEqual(tasks, [t3, t1, t2], "task with higher priority should be extracted first")
