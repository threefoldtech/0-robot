# THIS FILE IS SAFE TO EDIT. It will not be overwritten when rerunning go-raml.

from flask import jsonify, request
from zerorobot import config

from zerorobot.server import auth


@auth.admin.login_required
def ListWebHooksHandler():

    webhooks = config.webhooks
    output = []
    for wh in webhooks.list():
        output.append(wh.as_dict())

    return jsonify(output)

