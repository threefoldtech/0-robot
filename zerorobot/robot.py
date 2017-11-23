from js9 import j

from .service_collection import ServiceCollection
from .template_collection import TemplateCollection


class Robot:
    """
    A robot is the main context where the templates and service lives.
    It is responsible to:
        - run the REST API server
        - download the template from a git repository
        - load the templates in memory and make them available
    """

    def __init__(self):
        self._started = False
        self.template_repos = []
        self.data_repo = None

        self.templates_collection = TemplateCollection()
        self.service_collection = ServiceCollection()

    def add_template_repo(self, url):
        """
        add the template git repository to the robot
        It will clone the repository locally and load all the template from it
        """
        self.templates_collection.add_repo(url)

    def set_data_repo(self, url):
        """
        Set the url of the git repository to be used to serialize services state.
        It can be the same of one of the template repository used.
        """
        raise NotImplementedError()

    def create_service(self, template, name, data):
        """
        Instantiate a service from a template

        @param template: a template class
        @param name: name of the service, needs to be unique within the robot instance
        @param data: a dictionnary with the data of the service to create
        """
        raise NotImplementedError()

    def start(self):
        """
        start the rest web server
        load the services from the local git repository
        """
        raise NotImplementedError()

    def stop(self):
        """
        stop receiving requests
        gracefully stop all the services
        serialize all services state to disk
        """
        raise NotImplementedError()
