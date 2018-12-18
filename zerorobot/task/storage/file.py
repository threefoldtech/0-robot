import os

from Jumpscale import j

from .base import TaskStorageBase, TaskNotFoundError, TaskConflictError
from .import encoding


class TaskStorageFile(TaskStorageBase):
    """
    This class implement the TaskStorage interface
    using simple file on the local filesystem
    """

    def __init__(self, task_list):
        self.service = task_list.service
        # self._root = j.sal.fs.getTmpDirPath()
        self._root = os.path.join(self.service._path, 'tasks')
        if not os.path.exists(self._root):
            os.makedirs(self._root)
        self._count = 0

    def add(self, task):
        """
        save a task to the storage
        """
        self._count += 1
        j.sal.fs.writeFile(self._task_path(task), encoding.serialize_task(task))

    def get(self, guid):
        """
        find a task by guid
        """
        results = j.sal.fs.find(self._root, '*_%s' % guid)
        if len(results) <= 0:
            raise TaskNotFoundError("task %s not found" % guid)
        if len(results) > 1:
            raise TaskConflictError("found 2 tasks with same guid, this should not happen")
        return encoding.deserialize_task(j.sal.fs.readFile(results[0]), self.service)

    def list(self, from_timestap=None, to_timestap=None):
        """
        list all task. Optionally filter on time of creation
        from_timestamp: filter all task created before from_timetamp
        to_timestamp: filter all task created after to_timestamp
        """
        tasks = []
        for path in j.sal.fs.listFilesInDir(self._root):
            blob = j.sal.fs.readFile(path)
            task = encoding.deserialize_task(blob, self.service)
            if from_timestap and task.created < from_timestap:
                continue
            if to_timestap and task.created > to_timestap:
                continue
            tasks.append(task)
        return tasks

    def count(self):
        """
        return the number of task stored
        """
        return self._count

    def close(self):
        """
        gracefully close storage
        """
        pass

    def drop(self):
        """
        delete all the tasks
        """
        j.sal.fs.removeDirTree(self._root, True)
        j.sal.fs.createDir(self._root)
        self._count = 0

    def _task_path(self, task):
        return os.path.join(self._root, "%d_%s" % (self._count, task.guid))

