from zerorobot.client import Client
from zerorobot.service_proxy import ServiceProxy
from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol


class ZeroRobotClient:

    def __init__(self, base_url):
        self._client = Client(base_url)
        self._client.api.services.AddTaskToList
        self._is_local = False
        # TODO:  parse url and determine if local or not
        if base_url.find("localhost") != -1 or base_url.find("127.0.0.1") != -1:
            self._is_local = True
        else:
            self._client = Client(base_url)

    # def add_tempate_repo(self, url):
    #     if self._is_local()

    def create_service(self, template_name, service_name, data=None):
        """
        Instantiate a service from a template

        @param template_name: name of the template to use a base class for the service
        @param service_name: name of the service, needs to be unique within the robot instance
        @param data: a dictionnary with the data of the service to create
        """
        # if self._is_local:
        #     service = self._local_create_service(template_name, service_name, data)
        # else:
        service = self._remote_create_service(template_name, service_name, data)

        # scol.add(service)
        return service

    def _local_create_service(self, template_name, service_name, data=None):
        TemplateClass = tcol.get(template_name)
        service = TemplateClass(service_name)
        # todo: service.data = data
        return service

    def _remote_create_service(self, template_name, service_name, data=None):
        req = {
            "template": template_name,
            "version": "0.0.1",
            "name": service_name,
        }
        if data:
            req["data"] = data

        resp = self._client.api.services.createService(req)
        service = ServiceProxy(service_name, resp.data.guid, self._client)
        return service
