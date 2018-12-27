from Jumpscale import j

SCHEMA_TEMPLATE_REPOSITORY = """
@url = zrobot.template_repository
url = (S)
branch = (S)
"""

SCHEMA_TEMPLATE = """
@url = zrobot.template
uid = (S)
host = (S)
account = (S)
type = (S)
repository = (S)
name = (S)
version = (S)
"""

SCHEMA_SERVICE_STATE = """
@url = zrobot.service_state
category = (S)
tag = (S)
state = (S) #enum (ok,error,warning)
"""

SCHEMA_SERVICE = """
@url = zrobot.service
template = (S)
version = (S)
guid = (guid)
name = (S)
data = (bytes)
public = (B)
state = (LO) !zrobot.service_state
secret = (S)
"""

SCHEMA_ACTION = """
@url = zrobot.action
name = (S)
arguments = (LS)
"""

SCHEMA_TASK = """
@url = zrobot.task
action_name = (S)
# args = (dict)
template_name = (S)
service_name = (S)
service_guid = (guid)
guid = (guid)
state = (S) # is an enum = (new, ok, running, error)
created = (date)
duration = (I)
eco = (O) !zrobot.eco
result = (bytes)
"""

SCHEMA_ERROR = """
@url = zrobot.error
code = (I)
message = (S)
stack_trace = (S)
"""

SCHEMA_ECO = """
@url = zrobot.eco
cat = (s)
count  = (i)
message = (S)
message_pub = (S)
time_first = (I)
time_last = (I)
trace = (S)
description = (S)
"""

SCHEMA_REPOSITORY = """
@url = zrobot.repository
url = (url)
last_pushed = (date)
"""

SCHEMA_ROBOT_INFO = """
@url = zrobot.robot_info
config_repo = (O)!zrobot.repository
data_repo = (O)!zrobot.repository
type = (S) # enum = (node, digitalme)
storage_healthy = (B)
"""

SCHEMA_ROBOT_METRIC_CPU = """
@url = zrobot.robot_metrics.cpu
user = (F)
nice = (F)
system = (F)
idle = (F)
irq = (F)
softirq = (F)
"""

SCHEMA_ROBOT_METRIC_MEMORY = """
@url = zrobot.robot_metrics.memory
total = (F)
active = (F)
free = (F)
cached = (F)
swap_total = (F)
swap_free = (F)
"""

SCHEMA_ROBOT_METRICS = """
@url = zrobot.robot_metrics
cpu = (O) !zrobot.robot_metrics.cpu
memory = (O) !zrobot.robot_metrics.memory
nr_services = (I)
"""

SCHEMA_WEBHOOK = """
@url = zrobot.webhook
guid = (guid)
kind = (S) #enum = (eco)
url = (url)
"""

SCHEMA_LOG = """
@url = zrobot.log
# logs = (multiline) #TODO: multiline seems borken
logs = (S)
"""


SCHEMAS = [
    SCHEMA_TEMPLATE_REPOSITORY,
    SCHEMA_TEMPLATE,
    SCHEMA_SERVICE_STATE,
    SCHEMA_SERVICE,
    SCHEMA_ACTION,
    SCHEMA_TASK,
    SCHEMA_ECO,
    SCHEMA_ERROR,
    SCHEMA_REPOSITORY,
    SCHEMA_ROBOT_INFO,
    SCHEMA_ROBOT_METRIC_CPU,
    SCHEMA_ROBOT_METRIC_MEMORY,
    SCHEMA_ROBOT_METRICS,
    SCHEMA_LOG,
    SCHEMA_WEBHOOK,
]
