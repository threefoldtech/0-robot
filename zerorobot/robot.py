import importlib.util
import sys
import os

from js9 import j


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

        self._templates = {}
        self._services = {}

    def add_template_repo(self, url):
        """
        add the template git repository to the robot
        It will clone the repository locally and load all the template from it
        """
        for path in j.sal.fs.listFilesInDir(url, filter='*.py'):
            self._load_template(path)

    def _load_template(self, file_path):
        """
        load a template in memory from a file
        The file must contain a class that inherits from template.TemplateBase
        and the name of the class must match the name of the file.
        the name of the class is camelcased from the name of the file.
        ex:
            node.py -> Node
            vm_manager.py -> VmManager
            a_long_name.py -> ALongName
        """
        name = os.path.basename(file_path).split(os.path.extsep)[0]
        class_name = name.replace('_', ' ').title().replace(' ', '')

        spec = importlib.util.spec_from_file_location(name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if class_name not in module.__dict__:
            raise TemplateNameError("template %s should contain a class called %s" % (name, class_name))

        self._templates[name] = eval('module.%s' % class_name)

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
        if template not in self._templates:
            raise KeyError("template %s not loaded" % template)
        if name in self._services:
            raise ServiceExistError("a service with name %s already exists" % name)

        template_class = self._templates[template]
        service = template_class(name, data)

        for k, v in data.items():
            service.data[k] = v

        self._services[name] = service
        return service

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


class ServiceExistError(Exception):
    pass


class TemplateNameError(Exception):
    pass
