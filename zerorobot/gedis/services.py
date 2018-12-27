import os

from Jumpscale import j
from zerorobot import config
from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol
from zerorobot.server import auth
from zerorobot.task import TaskNotFoundError
from zerorobot.template.base import ActionNotFoundError, BadActionArgumentError
from zerorobot.template_collection import (TemplateConflictError,
                                           TemplateNotFoundError,
                                           ValidationError)

JSBASE = j.application.JSBaseClass


class services(JSBASE):

    def __init__(self):
        super().__init__()

    # TODO: would be nice to be able to send authentication details in some kind of headers
    # TODO: signature must be in a single line cause gedis code parsing doesn't support multine method definition
    def list(self, secrets, god_token=None, name=None, template_uid=None, template_host=None, template_account=None, template_repo=None, template_name=None, template_version=None):
        """
        ```in
        secrets = (LS)
        god_token = (S)
        name = (S)
        template_uid = (S)
        template_host = (S)
        template_account = (S)
        template_repo = (S)
        template_name = (S)
        template_version = (S)
        ````
        """
        # TODO: fix once gedis support list of objects
        # ```out
        # (LO)!zrobot.service
        # ```
        kwargs = {
            'name': name,
            'template_uid': template_uid,
            'template_host': template_host,
            'template_account': template_account,
            'template_repo': template_repo,
            'template_name': template_name,
            'template_version': template_version,
        }
        kwargs = {k: v for k, v in kwargs.items() if v}

        all_services = scol.find(**kwargs)

        if god_token and auth.god_jwt.verify(god_token):
            # god token passed, we list all the services
            return list(map(encode_service, all_services))

        # normal flow, only return service for which the user has the secret
        allowed_services_guids = auth.user_jwt.extract_service_guid_from_secrets(secrets)

        return list(map(encode_service, filter(
            lambda s: s.guid in allowed_services_guids or scol.is_service_public(s.guid),
            all_services)))

    def get(self, guid, secrets, god_token, schema_out):
        """
        ```in
        guid = (guid)
        secrets = (LS)
        god_token = (S)
        ```

        ```out
        !zrobot.service
        ```
        """
        if not can_access_service(guid, secrets, god_token):
            raise RuntimeError("no valid secret for this service")  # TODO: use proper exception

        service = scol.get_by_guid(guid)
        return encode_service(service)

    def create(self, service, schema_out):
        """
        ```in
        service = (O)!zrobot.service
        ```

        ```out
        !zrobot.service
        ```
        """
        TemplateClass = tcol.get(service.template)

        data = {}
        if service.data:
            data = j.data.serializers.msgpack.loads(service.data)
        service_created = tcol.instantiate_service(TemplateClass, service.name or None, data)

        try:
            secret = auth.user_jwt.create({'service_guid': service_created.guid})
        except auth.user_jwt.SigningKeyNotFoundError as err:
            return RuntimeError('error creating user secret: no signing key available')
        except Exception as err:
            return RuntimeError('error creating user secret: %s' % str(err))

        if service.public is True:
            scol.set_service_public(service_created.guid)

        return encode_service(service_created, secret)

    def delete(self, guid, secrets, god_token):
        """
        ```in
        guid = (guid)
        secrets = (LS)
        god_token = (S)
        ```
        """
        try:
            service = scol.get_by_guid(guid)

            if not can_access_service(guid, secrets, god_token):
                raise RuntimeError("no valid secret for this service")  # TODO: use proper exception

            service.delete()
        except scol.ServiceNotFoundError:
            pass
        return "OK"

    def actions(self, guid, secrets, god_token):
        """
        ```in
        guid = (guid)
        secrets = (LS)
        god_token = (S)
        ```
        """
        # FIXME: when gedis support list of schema out
        # ```out
        # (LO)!zrobot.action
        # ```
        if not can_access_service(guid, secrets, god_token):
            raise RuntimeError("no valid secret for this service")  # TODO: use proper exception

        service = scol.get_by_guid(guid)
        schema = j.data.schema.get(url='zrobot.action')
        out = []
        for action in get_actions_list(service):
            out.append(schema.get(data=action)._data)
        return out

    def logs(self, guid, secrets, god_token, schema_out):
        """
        ```in
        guid = (guid)
        secrets = (LS)
        god_token = (S)
        ```

        ```out
        !zrobot.log
        ```
        """
        if not can_access_service(guid, secrets, god_token):
            raise RuntimeError("no valid secret for this service")  # TODO: use proper exception

        service = scol.get_by_guid(guid)
        logs_obj = schema_out.new()

        log_file = os.path.join(j.dirs.LOGDIR, 'zrobot', service.guid)
        if j.sal.fs.exists(log_file):
            logs_obj.logs = j.sal.fs.fileGetContents(log_file)
        return logs_obj

    def tasks(self, guid, secrets, god_token, all=False):
        """
        ```in
        guid = (guid)
        secrets = (LS)
        god_token = (S)
        all = False (B)
        ```
        """
        if not can_access_service(guid, secrets, god_token):
            raise RuntimeError("no valid secret for this service")  # TODO: use proper exception

        service = scol.get_by_guid(guid)
        # return only task waiting or all existing task for this service
        return list(map(lambda t: encode_task(t, service)._data, service.task_list.list_tasks(all=all)))

    def task_create(self, guid, secrets, god_token, task, schema_out):
        """
        ```in
        guid = (guid)
        secrets = (LS)
        god_token = (S)
        task = (O)!zrobot.task
        ```

        ```out
        !zrobot.task
        ```
        """
        if not can_access_service(guid, secrets, god_token):
            raise RuntimeError("no valid secret for this service")  # TODO: use proper exception

        service = scol.get_by_guid(guid)
        # TODO: uncomment when dict is supported by schema
        # args = task.args or None
        try:
            # task = service.schedule_action(action=task.action_name, args=args)
            task = service.schedule_action(action=task.action_name, args=None)
        except ActionNotFoundError:
            raise RuntimeError("action '%s' not found" % task.action_name)
        except BadActionArgumentError as err:
            return ValueError(str(err))

        return encode_task(task, service)

    def task_get(self, guid, secrets, god_token, task_guid, schema_out):
        """
        ```in
        guid = (guid)
        secrets = (LS)
        god_token = (S)
        task_guid = (guid)
        ```

        ```out
        !zrobot.task
        ```
        """
        if not can_access_service(guid, secrets, god_token):
            raise RuntimeError("no valid secret for this service")  # TODO: use proper exception

        service = scol.get_by_guid(guid)
        task = service.task_list.get_task_by_guid(task_guid)

        return encode_task(task, service)


def encode_service(service, secret=None):
    service_schema = j.data.schema.get(url='zrobot.service')
    state_schema = j.data.schema.get(url='zrobot.service_state')

    service_obj = service_schema.new()
    service_obj.template = str(service.template_uid)
    service_obj.version = service.version
    service_obj.name = service.name
    service_obj.guid = service.guid
    for category, tag in service.state.categories.items():
        for tag, state in tag.items():
            state_obj = state_schema.new()
            state_obj.category = category
            state_obj.tag = tag
            state_obj.state = state
            service_obj.state.append(state_obj)
    service_obj.actions = []
    service_obj.public = scol.is_service_public(service.guid)
    # TODO: handle data, currently dict type is brokn in schema/gedis
    # if config.god:
    #     service.data.data = service.data
    if secret:
        service_obj.secret = secret
    return service_obj._data


def encode_task(task, service):
    encoded = j.data.schema.get(url='zrobot.task').new()

    result = b''
    eco = None

    if task.result is not None:
        result = j.data.serializers.msgpack.dumps(task.result)

    # TODO: fix when we can defined optional properties in schema
    task_data = task.eco.to_dict() if task.eco else {}
    eco = j.data.schema.get(url='zrobot.eco').get(data=task_data)

    encoded.template_name = service.template_name
    encoded.service_name = service.name
    encoded.service_guid = service.guid
    encoded.action_name = task.action_name
    encoded.state = task.state
    encoded.guid = task.guid
    encoded.created = task.created
    encoded.duration = task.duration or 0
    encoded.eco = eco
    encoded.result = result
    return encoded


def get_actions_list(obj):
    """
    extract the method name that the service has that are not the
    method comming from the template base
    """
    skip = ['load', 'save', 'schedule_action', 'recurring_action', 'validate', 'add_delete_callback']
    actions = []
    for name in dir(obj):
        if name in skip or name.startswith('_'):
            continue
        # test if the attribute is a property, we use this so we don't actually
        # call the property, but just detect it
        if isinstance(getattr(type(obj), name, None), property):
            actions.append({'name': name})
        elif callable(getattr(obj, name)):
            actions.append({'name': name})

    return actions


def can_access_service(guid, secrets, god_token):
    allowed_services_guids = auth.user_jwt.extract_service_guid_from_secrets(secrets)
    return auth.god_jwt.verify(god_token) if god_token else guid in allowed_services_guids


class ServiceCreateError(Exception):
    pass
