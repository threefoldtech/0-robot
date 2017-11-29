import os
from uuid import uuid4
from inspect import signature

from gevent.greenlet import Greenlet, GreenletExit

from .task import TaskList, Task
from zerorobot import service_collection as scol

# Error return when the argument pass when trying to schedule an action
# doesn't match with the method signature


class BadActionArgumentError(Exception):
    pass

# Error raised when trying to schedule an action that doesn't exist


class ActionNotFoundError(Exception):
    pass


class TemplateBase:
    """
    This is the base class any service should inherit from.

    The child class will implement actions on this class.
    """

    # The developer of the template need to set
    # the name and the version the template
    version = None
    template_name = None

    def __init__(self, name, guid=None):
        self.name = name
        self.guid = guid or str(uuid4())

        self.data = ServiceData()
        self.state = ServiceState()
        self.task_list = TaskList()

        # start the greenlet of this service
        self._gl = Greenlet(self._run)
        self._gl.start()

    def load(self, base_path):
        """
        load the service from it's file system serialized format

        @param base_path: path of the directory where
                          to save the service state and data
        """
        self.state.load(os.path.join(base_path, '_state.yaml'))
        self.data.load(os.path.join(base_path, '_data.yaml'))
        raise NotImplementedError()

    def save(self, base_path):
        """
        serialize the service state and data to a file

        @param base_path: path of the directory where
                          to save the service state and data
        """
        self.state.save(os.path.join(base_path, '_state.yaml'))
        self.data.save(os.path.join(base_path, '_data.yaml'))
        raise NotImplementedError()

    def _run(self):
        """
        _run is responsible to walk over the task list to execute actions
        and handle responses from other service
        """
        while True:
            try:
                # TODO: walk over the task list and execute actions
                task = self.task_list.get()
                task.execute()
            except GreenletExit:
                # TODO: gracefull shutdown
                print("stop service %s" % str(self))

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

    def __init__(self):
        super().__init__(self)
        self.capnp = None

    def save(self, path):
        """
        Serialize the data into a file

        @param path: file path where to save the data
        """
        raise NotImplementedError()

    def load(self, path):
        """
        Load the data from a file created by the save method

        @param path: file path from where to load the data
        """
        raise NotImplementedError()


class ServiceState:
    """
    This class represent the state of the service.
    """

    def __init__(self):
        pass

    def save(self, path):
        """
        Serialize the state into a file

        @param path: file path where to save the state
        """
        raise NotImplementedError()

    def load(self, path):
        """
        Load the state from a file created by the save method

        @param path: file path from where to load the state
        """
        raise NotImplementedError()
