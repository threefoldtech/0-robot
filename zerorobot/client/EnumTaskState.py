from enum import Enum


class EnumTaskState(Enum):
    new = "new"
    ok = "ok"
    running = "running"
    error = "error"
