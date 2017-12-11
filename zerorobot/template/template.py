import os
from uuid import uuid4
from inspect import signature

from gevent.greenlet import Greenlet, GreenletExit

from zerorobot.task import TaskList, Task
from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol
from zerorobot.template_collection import TemplateUID

from js9 import j


class BadActionArgumentError(Exception):
    """
    Error return when the argument pass when trying to schedule an action
    doesn't match with the method signature
    """
    pass


class ActionNotFoundError(Exception):
    """
    Error raised when trying to schedule an action that doesn't exist
    """
    pass


class BadTemplateError(Exception):
    """
    Error raised when trying to load a service with a wrong template class
    """
    pass


class TemplateBase:
    """
    This is the base class any service should inherit from.

    The child class will implement actions on this class.
    """

    # The developer of the template need to set the version the template
    version = None
    # This is the unique identifier of the template. This is set during template loading
    template_uid = None
    # path of the template on disk. This is set during template loading
    template_dir = None

    def __init__(self, name, guid=None):
        self.guid = guid or str(uuid4())
        self.name = name
        self.parent = None

        self.data = ServiceData(self)
        self.state = ServiceState()
        self.task_list = TaskList()

        # start the greenlet of this service
        self._gl = Greenlet(self._run)
        self._gl.start()

    @classmethod
    def load(cls, base_path):
        """
        load the service from it's file system serialized format

        @param base_path: path of the directory where
                          to load the service state and data from
        """
        if not os.path.exists(base_path):
            raise FileNotFoundError("Trying to load service from %s, but directory doesn't exists" % base_path)

        name = os.path.basename(base_path)
        service_info = j.data.serializer.yaml.load(os.path.join(base_path, 'service.yaml'))
        template_uid = TemplateUID.parse(service_info['template'])
        if template_uid != cls.template_uid:
            raise BadTemplateError("Trying to load service %s with template %s, while it requires %s"
                                   % (name, cls.template_uid, service_info['template']))

        if service_info['name'] != name:
            raise BadTemplateError("Trying to load service from folder %s, but name of the service is %s"
                                   % (base_path, service_info['name']))

        srv = cls(service_info['name'], service_info['guid'])
        if service_info['parent']:
            srv.parent = scol.get_by_guid(service_info['parent'])

        srv.state.load(os.path.join(base_path, 'state.yaml'))
        srv.data.load(os.path.join(base_path, 'data.yaml'))
        srv.task_list.load(os.path.join(base_path, 'tasks.yaml'), srv)

        return srv

    def save(self, base_path):
        """
        serialize the service state and data to a file

        @param base_path: path of the directory where
                          to save the service state and data
        return the path where the service is saved
        """
        parent = self.parent
        path = base_path
        while parent is not None:
            path = os.path.join(path, parent.name)
            parent = parent.parent

        path = os.path.join(path, self.name)

        os.makedirs(path, exist_ok=True)

        j.data.serializer.yaml.dump(os.path.join(path, 'service.yaml'), {
            'template': str(self.template_uid),
            'version': self.version,
            'name': self.name,
            'guid': self.guid,
            'parent': self.parent.guid if self.parent else None,
        })
        self.state.save(os.path.join(path, 'state.yaml'))
        self.data.save(os.path.join(path, 'data.yaml'))
        self.task_list.save(os.path.join(path, 'tasks.yaml'))
        return path

    def _run(self):
        """
        _run is responsible to walk over the task list to execute actions
        and handle responses from other service
        """
        while True:
            try:
                task = self.task_list.get()
                task.execute()
            except GreenletExit:
                # TODO: gracefull shutdown
                pass

    def schedule_action(self, action, args=None, resp_q=None):
        """
        Add an action to the task list of this service.
        This method should never be called directly by the user.
        It will always be called by another service.
        Or from a local service or from a remote service trough RPC

        @param action: action is the name of the action to add to the task list
        @param args: dictionnary of the argument to pass to the action
        @param resp_q: is the response queue on which the result of the action need to be put
        """
        if not hasattr(self, action):
            raise ActionNotFoundError("sel %s doesn't have action %s" % (self.name, action))

        method = getattr(self, action)
        if not callable(method):
            raise ActionNotFoundError("%s is not a function" % action)

        # make sure the argument we pass are correct
        s = signature(method)
        if args is not None:
            if len(args) != len(s.parameters):
                raise BadActionArgumentError()

            for param in s.parameters.values():
                if param.name not in args:
                    raise BadActionArgumentError()

        task = Task(self, action, args, resp_q)
        self.task_list.put(task)
        return task

    def delete(self):
        scol.delete(self)


class ServiceData(dict):
    """
    Small wrapper around dict object to make
    access to capnp object easy for the service
    """

    def __init__(self, service):
        """
        @param schema_path: path to the
        """
        path = os.path.join(service.template_dir, 'schema.capnp')
        if os.path.exists(path):
            schema_str = j.sal.fs.fileGetContents(path)
            msg = j.data.capnp.getObj(schema_str)
            self.update(msg.to_dict(verbose=True))

    def save(self, path):
        """
        Serialize the data into a file

        @param path: file path where to save the data
        """
        j.data.serializer.yaml.dump(path, dict(self))

    def load(self, path):
        """
        Load the data from a file created by the save method

        @param path: file path from where to load the data
        """
        self.update(j.data.serializer.yaml.load(path))


SERVICE_STATE_OK = 'ok'
SERVICE_STATE_ERROR = 'error'


class BadServiceStateError(Exception):
    """
    This exception is raised when trying to set a state to a value
    that is not supported
    """
    pass


class StateCategoryNotExistsError(Exception):
    """
    This exception is raised when trying to read the state of a
    category that doesn't exists
    """
    pass


class ServiceState:
    """
    This class represent the state of the service.
    """

    def __init__(self):
        self.categories = {}

    def set(self, category, tag, state):
        """
        set a state to a value.
        """
        if state not in [SERVICE_STATE_OK, SERVICE_STATE_ERROR]:
            raise BadServiceStateError("state not supported: %s" % state)

        if category not in self.categories:
            self.categories[category] = {}

        self.categories[category][tag] = state

    def get(self, category, tag=None):
        """
        get the value of a state
        """
        if category not in self.categories:
            raise StateCategoryNotExistsError("category %s does not exists" % category)

        # we don't filer on tag, early return
        if tag is None:
            return self.categories[category]

        if tag not in self.categories[category]:
            raise StateCategoryNotExistsError("tag %s does not exists in category %s" % (tag, category))

        # return only the state for this tag
        # we return a dict so it's consistent with the case when tag is None
        return {tag: self.categories[category][tag]}

    def save(self, path):
        """
        Serialize the state into a file

        @param path: file path where to save the state
        """
        j.data.serializer.yaml.dump(path, self.categories)

    def load(self, path):
        """
        Load the state from a file created by the save method

        @param path: file path from where to load the state
        """
        self.categories = j.data.serializer.yaml.load(path)

    def __repr__(self):
        return str(self.categories)

    __str__ = __repr__
