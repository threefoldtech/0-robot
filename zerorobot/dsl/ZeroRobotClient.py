from requests.exceptions import HTTPError

from zerorobot.client import Client
from zerorobot.service_proxy import ServiceProxy


class TemplateNotFoundError(Exception):
    """
    This exception is raised when trying to create a service
    from a template that doesn't exists
    """
    pass


class ServicesMgr:

    def __init__(self, robot):
        self._robot = robot
        self._client = robot._client

    def _instantiate(self, data):
        srv = ServiceProxy(data.name, data.guid, self._client)
        if data.parent:
            srv.parent = self._get(data.parent)
        return srv

    def _get(self, guid=None):
        resp = self._client.api.services.GetService(guid)
        return self._instantiate(resp.data)

    @property
    def names(self):
        """
        Return a dictionnary that contains all the service present on
        the ZeroRobot

        key is the name of the service
        value is a ServiceProxy object
        """
        services = {}
        resp = self._client.api.services.listServices()
        for service in resp.data:
            srv = self._instantiate(service)
            services[srv.name] = srv
        return services

    @property
    def guids(self):
        """
        Return a dictionnary that contains all the service present on
        the ZeroRobot

        key is the guid of the service
        value is a ServiceProxy object
        """
        services = {}
        resp = self._client.api.services.listServices()
        for service in resp.data:
            srv = self._instantiate(service)
            services[srv.guid] = srv
        return services

    def create(self, template_uid, service_name, data=None):
        """
        Instantiate a service from a template

        @param template_uid: UID of the template to use a base class for the service
        @param service_name: name of the service, needs to be unique within the robot instance
        @param data: a dictionnary with the data of the service to create
        """
        if template_uid not in self._robot.templates.uids:
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
        return service


class TemplatesMgr:

    def __init__(self, robot):
        self._robot = robot
        self._client = robot._client

    @property
    def uids(self):
        """
        Returns a list of template UID present on the ZeroRobot
        """
        resp = self._client.api.templates.ListTemplates()
        return {t.uid: t for t in resp.data}


class ZeroRobotClient:

    def __init__(self, base_url):
        self._client = Client(base_url)
        self.services = ServicesMgr(self)
        self.templates = TemplatesMgr(self)
