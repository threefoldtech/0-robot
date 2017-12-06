import json as JSON
import jsonschema
from jsonschema import Draft4Validator
from flask import Blueprint, jsonify, request

from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol
from zerorobot.service_collection import ServiceConflictError
from zerorobot.template import BadActionArgumentError, ActionNotFoundError

from js9 import j

import os
dir_path = os.path.dirname(os.path.realpath(__file__))

ServiceCreate_schema = JSON.load(open(dir_path + '/schema/ServiceCreate_schema.json'))
ServiceCreate_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', ServiceCreate_schema)
ServiceCreate_schema_validator = Draft4Validator(ServiceCreate_schema, resolver=ServiceCreate_schema_resolver)

Service_schema = JSON.load(open(dir_path + '/schema/Service_schema.json'))
Service_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', Service_schema)
Service_schema_validator = Draft4Validator(Service_schema, resolver=Service_schema_resolver)

TaskCreate_schema = JSON.load(open(dir_path + '/schema/TaskCreate_schema.json'))
TaskCreate_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', TaskCreate_schema)
TaskCreate_schema_validator = Draft4Validator(TaskCreate_schema, resolver=TaskCreate_schema_resolver)

Task_schema = JSON.load(open(dir_path + '/schema/Task_schema.json'))
Task_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', Task_schema)
Task_schema_validator = Draft4Validator(Task_schema, resolver=Task_schema_resolver)


services_api = Blueprint('services_api', __name__)


@services_api.route('/services', methods=['GET'])
def listServices():
    '''
    List all the services known by the ZeroRobot.
    It is handler for GET /services
    '''
    services = [service_view(s) for s in scol.list_services()]
    return JSON.dumps(services), 200, {"Content-type": 'application/json'}


@services_api.route('/services', methods=['POST'])
def createService():
    '''
    create a new service
    It is handler for POST /services
    '''
    inputs = request.get_json()
    try:
        ServiceCreate_schema_validator.validate(inputs)
    except jsonschema.ValidationError as e:
        print(e)
        return JSON.dumps({'code': 400, 'message': "bad request body"}), 400, {"Content-type": 'application/json'}

    try:
        TemplateClass = tcol.get(inputs['template'])
    except KeyError:
        return JSON.dumps({'code': 400, 'message': "template '%s' not found" % inputs['template']}), \
            400, {"Content-type": 'application/json'}
    except ValueError as err:
        return JSON.dumps({'code': 400, 'message': err.args[0]}), 400, {"Content-type": 'application/json'}

    try:
        service = tcol.instanciate_service(TemplateClass, inputs['name'], inputs.get('data', {}))
    except ServiceConflictError:
        service = None
        return JSON.dumps({'code': 409, 'message': "a service with name '%s' already exists" % inputs['name']}), \
            409, {"Content-type": 'application/json'}

    return JSON.dumps(service_view(service)), 201, {"Content-type": 'application/json'}


@services_api.route('/services/<service_guid>', methods=['GET'])
def GetService(service_guid):
    '''
    Get the detail of a service
    It is handler for GET /services/<service_guid>
    '''
    try:
        service = scol.get_by_guid(service_guid)
    except KeyError:
        return JSON.dumps({'code': 404, 'message': "service with guid '%s' not found" % service_guid}), \
            404, {"Content-type": 'application/json'}

    return JSON.dumps(service_view(service)), 200, {"Content-type": 'application/json'}


@services_api.route('/services/<service_guid>', methods=['DELETE'])
def DeleteService(service_guid):
    '''
    Delete a service
    It is handler for DELETE /services/<service_guid>
    '''

    try:
        service = scol.get_by_guid(service_guid)
        scol.delete(service)
    except KeyError:
        pass

    return "", 204, {"Content-type": 'application/json'}


@services_api.route('/services/<service_guid>/actions', methods=['GET'])
def ListActions(service_guid):
    '''
    List all the possible action a service can do.
    It is handler for GET /services/<service_guid>/actions
    '''

    try:
        service = scol.get_by_guid(service_guid)
    except KeyError:
        return JSON.dumps({'code': 404, 'message': "service with guid '%s' not found" % service_guid}), \
            404, {"Content-type": 'application/json'}

    actions = get_actions_list(service)

    return JSON.dumps(actions), 200, {"Content-type": 'application/json'}


@services_api.route('/services/<service_guid>/task_list', methods=['GET'])
def getTaskList(service_guid):
    '''
    Return all the action in the task list
    It is handler for GET /services/<service_guid>/task_list
    '''
    try:
        service = scol.get_by_guid(service_guid)
    except KeyError:
        return JSON.dumps({'code': 404, 'message': "service with guid '%s' not found" % service_guid}), \
            404, {"Content-type": 'application/json'}

    # return only task waiting or all existing task for this service
    all_task = request.args.get('all')
    if all_task is not None:
        all_task = j.data.types.bool.fromString(all_task)

    tasks = [task_view(t) for t in service.task_list.list_tasks(all=all_task)]

    return JSON.dumps(tasks), 200, {"Content-type": 'application/json'}


@services_api.route('/services/<service_guid>/task_list', methods=['POST'])
def AddTaskToList(service_guid):
    '''
    Add a task to the task list
    It is handler for POST /services/<service_guid>/task_list
    '''
    inputs = request.get_json()
    try:
        TaskCreate_schema_validator.validate(inputs)
    except jsonschema.ValidationError as e:
        print(e)
        return JSON.dumps({'code': 400, 'message': str(e)}), 400, {"Content-type": 'application/json'}

    try:
        service = scol.get_by_guid(service_guid)
    except KeyError:
        return JSON.dumps({'code': 404, 'message': "service with guid '%s' not found" % service_guid}), \
            404, {"Content-type": 'application/json'}

    args = inputs.get('args', None)
    try:
        task = service.schedule_action(action=inputs['action_name'], args=args)
    except ActionNotFoundError:
        return JSON.dumps({'code': 400, 'message': "action '%s' not found" % inputs['action_name']}), \
            400, {"Content-type": 'application/json'}
    except BadActionArgumentError:
        return JSON.dumps({'code': 400, 'message': "the argument passed in the requests, doesn't match the signature of the action"}), \
            400, {"Content-type": 'application/json'}

    return JSON.dumps(task_view(task)), 201, {"Content-type": 'application/json'}


@services_api.route('/services/<service_guid>/task_list/<task_guid>', methods=['GET'])
def GetTask(task_guid, service_guid):
    '''
    Retrieve the detail of a task
    It is handler for GET /services/<service_guid>/task_list/<task_guid>
    '''

    try:
        service = scol.get_by_guid(service_guid)
    except KeyError:
        return JSON.dumps({'code': 404, 'message': "service with guid '%s' not found" % service_guid}), \
            404, {"Content-type": 'application/json'}

    try:
        task = service.task_list.get_task_by_guid(task_guid)
    except KeyError:
        return JSON.dumps({'code': 404, 'message': "task with guid '%s' not found" % task_guid}), \
            404, {"Content-type": 'application/json'}

    return JSON.dumps(task_view(task)), 200, {"Content-type": 'application/json'}


def service_view(service):
    return {
        "template": str(service.template_uid),
        "version": service.version,
        "name": service.name,
        "guid": service.guid,
        "state": state_view(service.state),
        "actions": [],
    }


def state_view(state):
    out = []
    for category, tags in state.categories.items():
        for tag, state in tags.items():
            out.append({
                'category': category,
                'tag': tag,
                'state': state,
            })
    return out


def task_view(task):
    return {
        'template_name': task.service.template_name,
        'service_name': task.service.name,
        'service_guid': task.service.guid,
        'action_name': task.action_name,
        'state': task.state,
        'guid': task.guid,
        'created': task.created
    }


def get_actions_list(obj):
    """
    extract the method name that the service has that are not the
    method comming from the template base
    """
    skip = ['load', 'save', 'schedule_action']
    actions = []
    for name in dir(obj):
        if name in skip or name.startswith('_'):
            continue
        if callable(getattr(obj, name)):
            actions.append(name)
    return actions
