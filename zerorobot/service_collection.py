"""
this module is the only place where the service will be kept in memory.
other services and class need to use this module method to create, access, list and search the services
"""
import os

from js9 import j

from zerorobot.template_collection import TemplateUID

logger = j.logger.get('zerorobot')

_name_index = {}
_guid_index = {}


def add(service):
    if hasattr(service, 'name'):
        if service.name in _name_index:
            raise ServiceConflictError("a service with name=%s already exist" % service.name)
        _name_index[service.name] = service

    if hasattr(service, 'guid'):
        if service.guid in _name_index:
            raise ServiceConflictError("a service with guid=%s already exist" % service.guid)
        _guid_index[service.guid] = service

    logger.debug("add service %s to collection" % service)


def get_by_name(name):
    if name not in _name_index:
        raise KeyError("service with name=%s not found" % name)
    return _name_index[name]


def get_by_guid(guid):
    if guid not in _guid_index:
        raise KeyError("service with guid=%s not found" % guid)
    return _guid_index[guid]


def list_services():
    return list(_guid_index.values())


def delete(service):
    if hasattr(service, 'name') and service.name in _name_index:
        del _name_index[service.name]

    if hasattr(service, 'guid') and service.guid in _guid_index:
        del _guid_index[service.guid]

    logger.debug("delete service %s from collection" % service)


def load(template, base_path):
    """
    load the service from it's file system serialized format

    @param template: the template class to use to instantiate the service
    @param base_path: path of the directory where
                        to load the service state and data from
    """
    if not os.path.exists(base_path):
        raise FileNotFoundError("Trying to load service from %s, but directory doesn't exists" % base_path)

    name = os.path.basename(base_path)
    service_info = j.data.serializer.yaml.load(os.path.join(base_path, 'service.yaml'))
    template_uid = TemplateUID.parse(service_info['template'])
    if template_uid != template.template_uid:
        raise BadTemplateError("Trying to load service %s with template %s, while it requires %s"
                               % (name, template.template_uid, service_info['template']))

    if service_info['name'] != name:
        raise BadTemplateError("Trying to load service from folder %s, but name of the service is %s"
                               % (base_path, service_info['name']))

    srv = template(service_info['name'], service_info['guid'])
    if service_info['parent']:
        srv.parent = get_by_guid(service_info['parent'])

    srv.state.load(os.path.join(base_path, 'state.yaml'))
    srv.data.load(os.path.join(base_path, 'data.yaml'))
    srv.task_list.load(os.path.join(base_path, 'tasks.yaml'), srv)

    add(srv)
    return srv


class ServiceConflictError(Exception):
    pass


class BadTemplateError(Exception):
    """
    Error raised when trying to load a service with a wrong template class
    """
    pass
