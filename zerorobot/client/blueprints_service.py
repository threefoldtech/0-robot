
from .api_response import APIResponse
from .unmarshall_error import UnmarshallError

class BlueprintsService:
    def __init__(self, client):
        self.client = client



    def ExecuteBlueprint(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Execute a blueprint on the ZeroRobot
        It is method for POST /blueprints
        """
        uri = self.client.base_url + "/blueprints"
        return self.client.post(uri, data, headers, query_params, content_type)
