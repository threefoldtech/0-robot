import gevent
import signal

from js9 import j

from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol


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
        self.data_repo_url = None
        self._data_dir = None
        self._started = False
        self._sig_handler = []
        # self.templates_collection = TemplateCollection()

    def add_template_repo(self, url):
        """
        add the template git repository to the robot
        It will clone the repository locally and load all the template from it
        """
        tcol.add_repo(url)

    def set_data_repo(self, url):
        """
        Set the url of the git repository to be used to serialize services state.
        It can be the same of one of the template repository used.
        """
        self.data_repo_url = url
        location = j.clients.git.pullGitRepo(url=url)
        self._data_dir = j.sal.fs.joinPaths(location, 'zero_robot_data')

    def create_service(self, template_name, service_name, data):
        """
        Instantiate a service from a template

        @param template_name: name of the template to use a base class for the service
        @param service_name: name of the service, needs to be unique within the robot instance
        @param data: a dictionnary with the data of the service to create
        """
        TemplateClass = tcol.get_template(template_name)
        service = TemplateClass(service_name)
        # TODO: set data to the service
        # service.data = data
        scol.add_service(service)
        return service

    def start(self):
        """
        start the rest web server
        load the services from the local git repository
        """
        self._started = True

        self._sig_handler.append(gevent.signal(signal.SIGQUIT, self.stop))
        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))

        # For now there is no web server, we just
        # block on start
        def forever():
            while self._started:
                gevent.sleep(1)

        g = gevent.spawn(forever)
        g.join()

    def stop(self):
        """
        stop receiving requests
        gracefully stop all the services
        serialize all services state to disk
        """
        # prevent the signal handler to be called again is
        # more signal are received
        for h in self._sig_handler:
            h.cancel()

        self._started = False
        print('stopping robot')
