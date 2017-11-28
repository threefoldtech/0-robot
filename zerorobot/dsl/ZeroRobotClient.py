from zerorobot.template_collection import template_collection as tcol
from zerorobot.service_collection import service_collection as scol


class ZeroRobotClient:

    def __init__(self, base_url):
        self.base_url = base_url
        self._is_local = False
        # TODO: parse url and determine if local or not
        if self.base_url.find("localhost") != -1 or self.base_url.find("127.0.0.1") != -1:
            self._is_local = True

    def create_service(self, template_name, service_name, data):
        """
        Instantiate a service from a template

        @param template_name: name of the template to use a base class for the service
        @param service_name: name of the service, needs to be unique within the robot instance
        @param data: a dictionnary with the data of the service to create
        """
        service = None
        if self._is_local:
            service = self._local_create_service(template_name, service_name, data)
        else:
            service = self._remote_create_service(template_name, service_name, data)

        # keep service/proxy in memory
        scol.add_service(service)

        return service

    def _local_create_service(self, template_name, service_name, data):
        TemplateClass = tcol.get_template(template_name)
        service = TemplateClass(service_name)
        # TODO: set data to the service
        # service.data = data
        return service

    def _remote_create_service(self, template_name, service_name, data):
        """
        create a service on a remote ZeroRobot and a proxy locally then return the proxy
        """
        # Do a REST call on remote ZeroRobot
        # create the proxy service locally
        # return the proxy
        raise NotImplementedError()

    def ask_action(self, service, action, args):
        """
        Add an action on the task list of another service.

        @param service object: Service object. can be a local service or a proxy to a remote service
        @param action: action is the name of the action to add to the task list
        @param args: dictionnary of the argument to pass to the action
        """
        # if the service is a proxy, the schedule_action do a REST call on the remote ZeroRobot.
        # if it's local, we just add the task to the task list of the service directly
        service.schedule_action(action, args)
