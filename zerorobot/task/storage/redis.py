
from Jumpscale import j

from .base import TaskNotFoundError
from . import encoding


class TaskStorageRedis:
    """
    This class implement the TaskStorage interface
    using simple file on the local filesystem
    """

    def __init__(self, task_list):
        """
        create connection to the storage
        """
        super().__init__()
        self._service = task_list._service
        self._namespace = task_list._service.guid
        self._redis = j.clients.redis.get()

    def add(self, task):
        """
        save a task to the storage
        """
        self._redis.hset(self._namespace, task.guid, encoding.serialize_task(task))

    def get(self, guid):
        """
        find a task by guid
        """
        blob = self._redis.hget(self._namespace, guid)
        if blob:
            return encoding.deserialize_task(blob, self._service)
        raise TaskNotFoundError()

    def list(self, from_timestap=None, to_timestap=None):
        """
        list all task. Optionally filter on time of creation
        from_timestamp: filter all task created before from_timetamp
        to_timestamp: filter all task created after to_timestamp
        """
        tasks = []
        for blob in self._redis.hgetall(self._namespace).values():
            task = encoding.deserialize_task(blob, self._service)
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
        return self._redis.hlen(self._namespace)

    def close(self):
        """
        gracefully close storage
        """
        if self._redis:
            self._redis.delete(self._namespace)
            self._redis = None

    def _serialize_task(self, task):
        return j.data.serializers.json.dumps({
            "guid": task.guid,
            "action_name": task.action_name,
            "args": task._args,
            "state": task.state,
            "eco": task.eco.to_dict() if task.eco else None,
            "created": task.created,
            "duration": task.duration,
        })

    def _deserialize_task(self, blob):
        task = j.data.serializers.json.loads(blob)
        return _instantiate_task(task, self._service)

