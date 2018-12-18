"""
this module is the only place where the service will be kept in memory.
other services and class need to use this module method to create, access, list and search the services
"""
import os

from Jumpscale import j
from zerorobot.sqlite import SqliteIndex
from zerorobot.template_uid import TemplateUID

_sqlite_index = SqliteIndex()
_guid_index = {}


def add(service):
    if service.guid in _guid_index:
        raise ServiceConflictError(
            message="a service with guid=%s already exist" % service.guid,
            service=_guid_index[service.guid])
    _guid_index[service.guid] = service
    _sqlite_index.add_service(service)

    logger = j.logger.get('zerorobot')
    logger.debug("add service %s to collection" % service)


def find(**kwargs):
    guids = _sqlite_index.find(**kwargs)
    services = [_guid_index[guid] for guid in guids]
    return services


def get_by_name(name):
    services = find(name=name)
    if len(services) > 1:
        raise TooManyResults("more then one results for service name=%s, be more precise" % name)
    if len(services) < 1:
        raise ServiceNotFoundError("service with name=%s not found" % name)
    return services[0]


def get_by_guid(guid):
    if guid not in _guid_index:
        raise ServiceNotFoundError("service with guid=%s not found" % guid)
    return _guid_index[guid]


def list_services():
    return list(_guid_index.values())


def is_service_public(guid):
    """
    determine if a service is public or not

    :param service: guid of the service
    :type service: str
    :return: true is service is public, false otherwise
    :rtype: boolean
    """
    service = get_by_guid(guid)
    return getattr(service, '_public', False) is True


def set_service_public(guid):
    service = get_by_guid(guid)
    service._public = True


def delete(service):
    if service.guid in _guid_index:
        del _guid_index[service.guid]
    _sqlite_index.delete_service(service)

    logger = j.logger.get('zerorobot')
    logger.debug("delete service %s from collection" % service)


def load(template, service_detail):
    """
    load the service from it's file system serialized format

    @param template: the template class to use to instantiate the service
    @param service_detail:all the detail of a service in a dict (info, data, states, task list)
    """
    template_uid = TemplateUID.parse(service_detail['service']['template'])
    guid = service_detail['service']['guid']
    try:
        if template_uid > template.template_uid:
            raise BadTemplateError("Trying to load service %s with template %s, while it requires %s or higher" % (guid, template.template_uid, service_detail['service']['template']))
    except ValueError:  # is the two template are not the same, ValueError is raised
        raise BadTemplateError("Trying to load service %s with template %s, while it requires %s or higher" % (guid, template.template_uid, service_detail['service']['template']))

    service = template(name=service_detail['service']['name'], guid=guid, data=service_detail['data'])
    service._public = service_detail['service'].get('public', False)

    service.state.load(service_detail['states'])
    # srv.data.load(service_detail['data']) FIXME: should we need this since we pass the data in the constructor line 94
    tasks = service_detail.get('tasks') or []
    service.task_list.load(tasks)
    add(service)
    return service


def upgrade(service, new_template, force=False):
    if not force and service.template_uid == new_template.template_uid:
        # nothing to do
        return service

    logger = j.logger.get('zerorobot')
    logger.info("upgrade service %s (%s) to %s", service.name, service.guid, new_template.template_uid)
    service.template_uid = new_template.template_uid

    # if there is a task running for this service, wait for it to finish, before stopping the service
    current_task = service.task_list.current
    if current_task is not None:
        current_task.wait(timeout=300)  # FIXME: fixed timeout, no timeout ?

    # stop the services
    service.gl_mgr.stop_all(wait=True)
    service.save()

    # remove service from memory
    delete(service)

    # create new instance of the service with updated version of the template
    new_service = new_template(name=service.name, guid=service.guid, data=service.data)
    new_service._public = service._public

    new_service.state = service.state
    # new_service.task_list = service.task_list
    add(new_service)

    new_service.save()
    return new_service


def drop_all():
    """
    delete all services
    """
    for s in list_services():
        delete(s)
    _guid_index = {}


class ServiceConflictError(Exception):
    """
    Raised when trying to create a service with a duplicate name

    @param service: the conflicting service that already exists
    """

    def __init__(self, message, service):
        super().__init__(message)
        self.service = service


class TooManyResults(Exception):
    """
    Raised when trying to get a specific service and the
    search retunr more then 1 results
    """
    pass


class BadTemplateError(Exception):
    """
    Error raised when trying to load a service with a wrong template class
    """
    pass


class ServiceNotFoundError(KeyError):
    """
    Raised when trying to get a service that doesn't exists
    """

