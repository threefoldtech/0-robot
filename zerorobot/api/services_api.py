import json as JSON
import jsonschema
from jsonschema import Draft4Validator
from flask import Blueprint, jsonify, request

from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol
from zerorobot.service_collection import ServiceConflictError


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
        return JSON.dumps({'code': 400, 'message': "bad request body"}), 400, {"Content-type": 'application/json'}

    try:
        TemplateClass = tcol.get_template(inputs['template'])
    except KeyError:
        return JSON.dumps({'code': 400, 'message': "template '%s' not found" % inputs['template']}), \
            400, {"Content-type": 'application/json'}

    service = TemplateClass(inputs['name'])
    try:
        scol.add_service(service)
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


@services_api.route('/services/<service_guid>/actions', methods=['GET'])
def ListActions(service_guid):
    '''
    List all the possible action a service can do.
    It is handler for GET /services/<service_guid>/actions
    '''

    return jsonify()


@services_api.route('/services/<service_guid>/task_list', methods=['GET'])
def getTaskList(service_guid):
    '''
    Return all the action in the task list
    It is handler for GET /services/<service_guid>/task_list
    '''

    inputs = request.get_json()
    try:
        Task_schema_validator.validate(inputs)
    except jsonschema.ValidationError as e:
        return jsonify(errors="bad request body"), 400

    return jsonify()


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
        return jsonify(errors="bad request body"), 400

    return jsonify()


@services_api.route('/services/<service_guid>/task_list/<task_guid>', methods=['GET'])
def GetTask(task_guid, service_guid):
    '''
    Retrieve the detail of a task
    It is handler for GET /services/<service_guid>/task_list/<task_guid>
    '''

    return jsonify()


def service_view(service):
    return {
        "template": service.template_name,
        "version": service.version,
        "name": service.name,
        "guid": service.guid,
        "state": {},
        "actions": [],
    }
