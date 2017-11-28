import json as JSON
import jsonschema
from jsonschema import Draft4Validator
from flask import Blueprint, jsonify, request

from zerorobot import template_collection as tcol


import os
dir_path = os.path.dirname(os.path.realpath(__file__))

TemplateRepository_schema = JSON.load(open(dir_path + '/schema/TemplateRepository_schema.json'))
TemplateRepository_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', TemplateRepository_schema)
TemplateRepository_schema_validator = Draft4Validator(TemplateRepository_schema, resolver=TemplateRepository_schema_resolver)


templates_api = Blueprint('templates_api', __name__)


@templates_api.route('/templates', methods=['GET'])
def ListTemplates():
    '''
    List all the templates available to the ZeroRobot
    It is handler for GET /templates
    '''
    templates = [template_view(t) for t in tcol.list_templates()]
    return JSON.dumps(templates), 200, {"Content-type": 'application/json'}


@templates_api.route('/templates', methods=['POST'])
def AddTemplateRepo():
    '''
    Clone a template repository and make the templates available to the ZeroRobot
    It is handler for POST /templates
    '''
    inputs = request.get_json()
    try:
        TemplateRepository_schema_validator.validate(inputs)
    except jsonschema.ValidationError as e:
        return JSON.dumps({'code': 400, 'message': "bad request body"}), 400, {"Content-type": 'application/json'}

    # TODO: handle branches
    added = tcol.add_repo(inputs['url'])
    templates = [template_view(t) for t in added]
    return JSON.dumps(templates), 201, {"Content-type": 'application/json'}


def template_view(template):
    return {
        "name": template.template_name,
        "version": template.version
    }
