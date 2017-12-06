from zerorobot.client import Client
from zerorobot.service_proxy import ServiceProxy
from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol

from requests.exceptions import HTTPError


class TemplateNotFoundError(Exception):
    """
    This exception is raised when trying to create a service
    from a template that doesn't exists
    """
    pass


class ZeroRobotClient:

    def __init__(self, base_url):
        self._client = Client(base_url)
        self._services = None

    @property
    def services(self):
        """
        Return a dictionnary that contains all the service present on
        the ZeroRobot

        key is the name of the service
        value is a ServiceProxy object
        """
        if self._services is None:
            self._services = {}
            resp = self._client.api.services.listServices()
            for service in resp.data:
                service = ServiceProxy(service.name, service.guid, self._client)
                self._services[service.name] = service
        return self._services

    def create_service(self, template_uid, service_name, data=None):
        """
        Instantiate a service from a template

        @param template_uid: UID of the template to use a base class for the service
        @param service_name: name of the service, needs to be unique within the robot instance
        @param data: a dictionnary with the data of the service to create
        """
        if template_uid not in self.templates:
            raise TemplateNotFoundError("template %s not found" % template_uid)

        req = {
            "template": template_uid,
            "version": "0.0.1",
            "name": service_name,
        }
        if data:
            req["data"] = data

        try:
            resp = self._client.api.services.createService(req)
        except HTTPError as err:
            print(err.response.json())
            raise err

        service = ServiceProxy(service_name, resp.data.guid, self._client)
        if self._services is None:
            self._services = {}
        self._services[service.name] = service
        return service

    @property
    def templates(self):
        """
        Returns a list of template UID present on the ZeroRobot
        """
        resp = self._client.api.templates.ListTemplates()
        return [t.uid for t in resp.data]
