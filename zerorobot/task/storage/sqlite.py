from .base import TaskStorageBase, TaskNotFoundError, TaskConflictError
from zerorobot.task.utils import _instantiate_task
import os
import sqlite3
import msgpack
from jumpscale import j

logger = j.logger.get(__name__)

_create_table_stmt = """
CREATE TABLE IF NOT EXISTS tasks (
    guid TEXT PRIMARY KEY UNIQUE,
    created INTEGER,
    payload BLOB
)
"""

_create_index_stmts = [
    "CREATE INDEX IF NOT EXISTS guid ON tasks (guid)",
    "CREATE INDEX IF NOT EXISTS created ON tasks (created)",
]

_add_task_stmt = "INSERT INTO tasks VALUES (?,?,?)"
_delete_task_stmt = "DELETE FROM tasks WHERE guid IN (SELECT guid FROM tasks WHERE created < ? )"
_find_task_stmt = "SELECT * FROM tasks"
_count_tasks_stmt = "SELECT count(*) FROM tasks"
_drop_stmt = "DELETE FROM tasks"


class TaskStorageSqlite(TaskStorageBase):
    """
    This class implement the TaskStorage interface
    using sqlite
    """

    def __init__(self, task_list):
        self._opened = False

        self.service = task_list.service
        db_path = os.path.join(self.service._path, 'tasks.db')
        if not os.path.exists(self.service._path):
            os.makedirs(self.service._path)
        self.conn = sqlite3.connect(db_path)
        self._opened = True
        self._create_table()

    @property
    def is_open(self):
        return self._opened

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(_create_table_stmt)
        for stmt in _create_index_stmts:
            cursor.execute(stmt)

    def add(self, task):
        """
        save a task to the storage
        """
        cursor = self.conn.cursor()
        t = (task.guid,
             task.created,
             self._serialize_task(task))
        try:
            cursor.execute(_add_task_stmt, t)
            cursor.connection.commit()
        except sqlite3.IntegrityError:
            raise TaskConflictError("task %s already exists", task.guid)

    def get(self, guid):
        """
        find a task by guid
        """
        cursor = self.conn.cursor()
        stmt = _find_task_stmt + ' WHERE guid=?'
        cursor.execute(stmt, (guid,))
        result = cursor.fetchone()
        if not result:
            raise TaskNotFoundError("task %s not found" % guid)
        task = self._deserialize_task(result[2])
        task['guid'] = guid
        task = _instantiate_task(task, self.service)
        return task

    def list(self, from_timestap=None, to_timestap=None):
        """
        list all task. Optionally filter on time of creation
        from_timestamp: filter all task created before from_timetamp
        to_timestamp: filter all task created after to_timestamp
        """
        cursor = self.conn.cursor()
        stmt = _find_task_stmt
        args = None
        if from_timestap and not to_timestap:
            stmt += ' WHERE created >= ? '
            args = (from_timestap,)
        elif to_timestap and not from_timestap:
            stmt += ' WHERE created <= ? '
            args = (to_timestap,)
        elif from_timestap and to_timestap:
            stmt += ' WHERE created >= ? AND created <= ?'
            args = (from_timestap, to_timestap)

        if args:
            cursor.execute(stmt, args)
        else:
            cursor.execute(stmt)

        tasks = []
        for result in cursor.fetchall():
            task = self._deserialize_task(result[2])
            task['guid'] = result[0]
            task = _instantiate_task(task, self.service)
            tasks.append(task)
        return tasks

    def count(self):
        """
        return the number of task stored
        """
        cursor = self.conn.cursor()
        return cursor.execute(_count_tasks_stmt).fetchone()[0]

    def close(self):
        """
        gracefully close storage
        """
        cursor = self.conn.cursor()
        if self.is_open:
            conn = cursor.connection
            cursor.close()
            conn.close()
            self._opened = False

    def delete_until(self, to_timestap):
        cursor = self.conn.cursor()
        cursor.execute(_delete_task_stmt, (to_timestap,))
        cursor.connection.commit()
        # call vacuum to reclaim disk space after deletion of a bunch of tasks
        cursor.execute("VACUUM")

    def drop(self):
        """
        delete all the tasks
        """
        cursor = self.conn.cursor()
        cursor.execute(_drop_stmt)
        cursor.connection.commit()

    def _serialize_task(self, task):
        return msgpack.dumps({
            'action_name': task.action_name,
            'args': task._args,
            'result': task.result,
            "created": task.created,
            'duration': task.duration,
            'eco': task.eco.to_dict() if task.eco else None,
            'state': task.state
        })

    def _deserialize_task(self, blob):
        return msgpack.loads(blob, raw=False)
