import unittest

from zerorobot.task import PRIORITY_NORMAL, PRIORITY_SYSTEM, Task, TaskList


class FakeService:

    def __init__(self, name):
        self.name = name


class TestTaskList(unittest.TestCase):

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
        t = Task(FakeService("s1"), "foo", {})
        tl.put(t)
        self.assertFalse(tl.empty())
        t2 = tl.get()
        self.assertEqual(t, t2, "task extracted from the list should be the same as the task added")
        self.assertEqual(tl._done[0], t, "task extracted from the list should be kept in the _done list")

    def test_get(self):
        tl = TaskList()

        t1 = Task(FakeService("s1"), "foo", {})
        t2 = Task(FakeService("s2"), "bar", {})
        t3 = Task(FakeService("s3"), "bar", {})

        tl.put(t1)
        tl.put(t2)
        tl.put(t3)

        tasks = []
        while not tl.empty():
            tasks.append(tl.get())
        self.assertEqual(tasks, [t1, t2, t3])

    def test_get_by_guid(self):
        tl = TaskList()

        t1 = Task(FakeService("s1"), "foo", {})
        t2 = Task(FakeService("s2"), "bar", {})
        t3 = Task(FakeService("s3"), "bar", {})

        tl.put(t1)
        tl.put(t2)
        tl.put(t3)

        task = tl.get_task_by_guid(t1.guid)
        self.assertEqual(task, t1)
        with self.assertRaises(KeyError):
            tl.get_task_by_guid('1111')

    def test_list(self):
        tl = TaskList()
        t1 = Task(FakeService("s1"), "foo", {})
        t2 = Task(FakeService("s2"), "bar", {})
        tl.put(t1)
        tl.put(t2)

        tasks = tl.list_tasks()
        self.assertEqual(tasks, [t1, t2], "listing of tasks should return all enqueued tasks")

        _ = tl.get()
        tasks = tl.list_tasks()
        self.assertEqual(tasks, [t2], "listing of tasks should return all enqueued tasks")

        all_tasks = tl.list_tasks(all=True)
        self.assertEqual(all_tasks, [t2, t1], "listing of all tasks should return all enqueued tasks and all done tasks")

    def test_priority(self):
        tl = TaskList()

        t1 = Task(FakeService("s1"), "foo", {})
        t2 = Task(FakeService("s2"), "bar", {})
        t3 = Task(FakeService("s3"), "foo", {})

        tl.put(t1, priority=PRIORITY_NORMAL)
        tl.put(t2, priority=PRIORITY_NORMAL)
        tl.put(t3, priority=PRIORITY_SYSTEM)

        tasks = []
        while not tl.empty():
            tasks.append(tl.get())

        self.assertEqual(tasks, [t3, t1, t2], "task with higher priority should be extracted first")
