from jumpscale import j

from zerorobot.task.utils import _instantiate_task


def serialize_task(task):
    return j.data.serializer.json.dumps({
        "guid": task.guid,
        "action_name": task.action_name,
        "args": task._args,
        "state": task.state,
        "eco": task.eco.to_dict() if task.eco else None,
        "result": task.result,
        "created": task.created,
        "duration": task.duration,
    })


def deserialize_task(blob, service):
    task = j.data.serializer.json.loads(blob)
    return _instantiate_task(task, service)
