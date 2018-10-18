"""
This module expose the high level API that is meant to be used by service developer in the template actions.

It provie ways to create and list services from a group of ZeroRobots in a unified way.
"""

from jumpscale import j
from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol
from zerorobot.dsl.ZeroRobotManager import ZeroRobotManager
from zerorobot.template_collection import TemplateNotFoundError
from zerorobot.template_uid import TemplateUID

from . import config_mgr


class ServicesMgr:

    def __init__(self):
        pass

    @property
    def names(self):
        """
        Return a dictionnary that contains all the service present on the local 0-robot

        key is the name of the service
        value is a Service
        """
        services = {s.name: s for s in scol.list_services()}
        return services

    @property
    def guids(self):
        """
        Return a dictionnary that contains all the service present on the local 0-robot

        key is the guid of the service
        value is a Service
        """
        return scol._guid_index

    def find(self, **kwargs):
        """
        Search for services and filter results from kwargs.
        You can filter on:
        "name", "template_uid", "template_host", "template_account", "template_repo", "template_name", "template_version"

        example: to list all services with name foo: find(name='foo')
        """
        services = {}
        for service in scol.find(**kwargs):
            services[service.guid] = service

        return list(services.values())

    def exists(self, **kwargs):
        """
        Test if a service exists and filter results from kwargs.
        You can filter on:
        "name", "template_uid", "template_host", "template_account", "template_repo", "template_name", "template_version"
        """
        results = self.find(**kwargs)
        return len(results) > 0

    def get(self, **kwargs):
        """
        return a service service based on the filters in kwargs.
        You can filter on:
        "name", "template_uid", "template_host", "template_account", "template_repo", "template_name", "template_version"
        """
        results = self.find(**kwargs)
        i = len(results)
        if i > 1:
            raise scol.TooManyResults("%d services found" % i)
        elif i <= 0:
            raise scol.ServiceNotFoundError("service not found: query was: %s" % str(kwargs))
        return results[0]

    def create(self, template_uid, service_name=None, data=None, public=False):
        """
        Instantiate a service from a template on the local 0-robot

        :param template_uid: UID of the template to use a base class for the service
        :type template_uid: str
        :param service_name: name of the service, needs to be unique within the robot instance. If not specified a name is genrated, defaults to None
        :type service_name: str, optional
        :param data: data of the service to create, defaults to None
        :type data: dict
        :param public: is set to true, the service will be public, so anyone can schedule action on it, defaults to False
        :type public: bool, optional
        :return: the service created
        :rtype: Service object of the type of the template
        """
        # we can create a service locally, the local robot has the template
        template = tcol.get(template_uid)
        service = tcol.instantiate_service(template, service_name, data)
        if public:
            scol.set_service_public(service.guid)
        return service

    def find_or_create(self, template_uid, service_name, data, public=False):
        """
        Helper method that first check if a service exists and if not then creates it
        if the service is found, it is returned
        if the service is not found, it is created using the data passed then returned

        :param template_uid: UID of the template to use a base class for the service
        :type template_uid: str
        :param service_name: name of the service, needs to be unique within the robot instance. If not specified a name is genrated, defaults to None
        :type service_name: str, optional
        :param data: a dictionnary with the data of the service if and only if the service is created
                     so if the service already exists, the data argument is not used, defaults to None
        :type data: dict
        :param public: is set to true, the service will be public, so anyone can schedule action on it, defaults to False
        :type public: bool, optional
        :return: the service created
        :rtype: Service object of the type of the template
        """
        try:
            return self.get(template_uid=template_uid, name=service_name)
        except scol.ServiceNotFoundError:
            return self.create(template_uid=template_uid, service_name=service_name, data=data, public=public)


class TemplatesMgr:

    def __init__(self):
        pass

    def add_repo(self, url, branch='master'):
        """
        Add a new template repository

        returns the templates that were added from this repository
        """
        return tcol.add_repo(url=url, branch=branch)

    def checkout_repo(self, url, revision='master'):
        """
        Checkout a branch/tag/revision of a template repository

        @param url: url of the template repo
        @param revision: branch, tag or revision to checkout
        """
        return tcol.checkout_repo(url, revision)

    @property
    def uids(self):
        """
        Returns a dict of template UID present on the ZeroRobot
        keys are the templates uids
        values are the templates objects
        """
        return tcol._templates


class ZeroRobotAPI:
    # TODO: find better name

    def __init__(self):
        self.services = ServicesMgr()
        self.templates = TemplatesMgr()
        self.robots = config_mgr
