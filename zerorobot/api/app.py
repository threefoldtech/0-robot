import os

from flask import Flask, send_file, send_from_directory

from .blueprints_api import blueprints_api
from .services_api import services_api
from .templates_api import templates_api

app = Flask(__name__)

app.register_blueprint(blueprints_api)
app.register_blueprint(services_api)
app.register_blueprint(templates_api)

dir_path = os.path.dirname(os.path.realpath(__file__))


@app.route('/apidocs/<path:path>')
def send_js(path):
    return send_from_directory(dir_path + '/apidocs', path)


@app.route('/', methods=['GET'])
def home():
    return send_file('index.html')

if __name__ == "__main__":
    app.run(debug=True)
