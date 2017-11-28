import json as JSON
import jsonschema
from jsonschema import Draft4Validator
from flask import Blueprint, jsonify, request


import os
dir_path = os.path.dirname(os.path.realpath(__file__))

Blueprint_schema = JSON.load(open(dir_path + '/schema/Blueprint_schema.json'))
Blueprint_schema_resolver = jsonschema.RefResolver('file://' + dir_path + '/schema/', Blueprint_schema)
Blueprint_schema_validator = Draft4Validator(Blueprint_schema, resolver=Blueprint_schema_resolver)


blueprints_api = Blueprint('blueprints_api', __name__)


@blueprints_api.route('/blueprints', methods=['POST'])
def ExecuteBlueprint():
    '''
    Execute a blueprint on the ZeroRobot
    It is handler for POST /blueprints
    '''

    inputs = request.get_json()
    try:
        Blueprint_schema_validator.validate(inputs)
    except jsonschema.ValidationError as e:
        return jsonify(errors="bad request body"), 400

    return jsonify()
