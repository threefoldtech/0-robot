# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

import os
from flask import jsonify, request, Response
from jumpscale import j
from zerorobot import service_collection as scol
from zerorobot import config
from zerorobot.server import auth


def GetLogsHandler(service_guid):
    if not auth.god_jwt.check_god_token(request):
        return jsonify(code=400, message='god mode is not enabled on the service, you cannot read the logs'), 400

    try:
        service = scol.get_by_guid(service_guid)
    except KeyError:
        return jsonify(code=404, message="service with guid '%s' not found" % service_guid), 404

    log_file = os.path.join(j.dirs.LOGDIR, 'zrobot', service.guid)
    if not os.path.exists(log_file):
        return jsonify(logs=''), 200

    with open(log_file) as f:
        return jsonify(logs=f.read()), 200
