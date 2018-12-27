"""
This module implement the ServiceProxy class.

This class is used to provide a local proxy to a remote service for a ZeroRobot.
When a service or robot ask the creation of a service to another robot, a proxy class is created locally
so the robot see the service as if it as local to him while in reality the service is managed by another robot.
"""

import urllib

from requests.exceptions import HTTPError

from jose import jwt
from Jumpscale import j
from zerorobot.dsl import config_mgr
from zerorobot.errors import Eco
from zerorobot.task import (TASK_STATE_ERROR, TASK_STATE_NEW, TASK_STATE_OK,
                            TASK_STATE_RUNNING, Task, TaskNotFoundError)
from zerorobot.template.state import ServiceState

logger = j.logger.get(__name__)


class ServiceProxyGedis:
    def __init__(self, name, guid, http_client, gedis_client):
        """
        @param name: name of the service
        @param guid: guid of the service
        @param gedis_client: Instance of ZeroRobotClient that talks to the robot on which the
                              service is actually running
        """
        self._http_client = http_client
        self._gedis_client = gedis_client
        self.name = name
        self.guid = guid
        self.template_uid = None
        # a proxy service doesn't have direct access to the data of it's remote homologue
        # cause data are always only accessible  by the service itself and locally
        self._data = None
        self.task_list = TaskListProxyGedis(self)

    def __repr__(self):
        # Provide a nice representation in tools like IPython / js9
        return "robot://%s/%s?%s" % (self._gedis_client._client.config.instance, self.template_uid, urllib.parse.urlencode(dict(name=self.name, guid=self.guid)))

    @property
    def data(self):
        return self._data

    @property
    def state(self):
        kwargs = {
            'secrets': self._http_client.config.data['secrets_'],
            'god_token': self._http_client.config.data['god_token_'],
            'guid': self.guid
        }
        service = self._gedis_client.services.get(**kwargs)
        s = ServiceState()
        for state in service.state:
            s.set(state.category, state.tag, state.state.value)
        return s

    @property
    def actions(self):
        """
        list available actions of the services
        """
        kwargs = {
            'secrets': self._http_client.config.data['secrets_'],
            'god_token': self._http_client.config.data['god_token_'],
            'guid': self.guid
        }
        schema = j.data.schema.get(url='zrobot.action')
        actions = list(map(lambda x: schema.get(capnpbin=x), self._gedis_client.services.actions(**kwargs)))
        return sorted([a.name for a in actions])

    @property
    def logs(self):
        kwargs = {
            'secrets': self._http_client.config.data['secrets_'],
            'god_token': self._http_client.config.data['god_token_'],
            'guid': self.guid
        }
        logs = self._gedis_client.services.logs(**kwargs)
        return logs.logs

    def schedule_action(self, action, args=None):
        """
        Do a call on a remote ZeroRobot to add an action to the task list of
        the corresponding service

        @param action: action is the name of the action to add to the task list
        @param args: dictionnary of the argument to pass to the action
        """
        task_data = {
            "action_name": action,
        }
        # TODO: uncomment when gedis support dict type
        # if args:
        #     task_data["args"] = args

        task_creation = j.data.schema.get(url='zrobot.task').get(data=task_data)
        kwargs = {
            'secrets': self._http_client.config.data['secrets_'],
            'god_token': self._http_client.config.data['god_token_'],
            'guid': self.guid,
            'task': task_creation,
            'guid': self.guid,
        }

        task = self._gedis_client.services.task_create(**kwargs)
        return _task_proxy_from_gedis(task, self)

    def delete(self):
        kwargs = {
            'secrets': self._http_client.config.data['secrets_'],
            'god_token': self._http_client.config.data['god_token_'],
            'guid': self.guid
        }
        self._gedis_client.services.delete(**kwargs)
        # clean up secret from zrobot client
        config_mgr.remove_secret(self._http_client.instance, self.guid)


class ServiceProxy():
    """
    This class is used to provide a local proxy to a remote service for a ZeroRobot.
    When a service or robot ask the creation of a service to another robot, a proxy class is created locally
    so the robot see the service as if it as local to him while in reality the service is managed by another robot.
    """

    def __init__(self, name, guid, zrobot_client):
        """
        @param name: name of the service
        @param guid: guid of the service
        @param zrobot_client: Instance of ZeroRobotClient that talks to the robot on which the
                              service is actually running
        """
        self._zrobot_client = zrobot_client
        self.name = name
        self.guid = guid
        self.template_uid = None
        # a proxy service doesn't have direct access to the data of it's remote homologue
        # cause data are always only accessible  by the service itself and locally
        self._data = None
        self.task_list = TaskListProxy(self)

    def __repr__(self):
        # Provide a nice representation in tools like IPython / js9
        return "robot://%s/%s?%s" % (self._zrobot_client.instance, self.template_uid, urllib.parse.urlencode(dict(name=self.name, guid=self.guid)))

    @property
    def data(self):
        return self._data

    @property
    def state(self):
        # TODO: handle exceptions
        service, _ = self._zrobot_client.api.services.GetService(self.guid)
        s = ServiceState()
        for state in service.state:
            s.set(state.category, state.tag, state.state.value)
        return s

    @property
    def actions(self):
        """
        list available actions of the services
        """
        actions, _ = self._zrobot_client.api.services.ListActions(self.guid)
        return sorted([a.name for a in actions])

    @property
    def logs(self):
        try:
            logs, resp = self._zrobot_client.api.services.GetLogs(self.guid)
        except HTTPError as err:
            if err.response.status_code == 400:
                raise RuntimeError(err.response.json()['message'])
            raise err

        return logs.logs

    def schedule_action(self, action, args=None):
        """
        Do a call on a remote ZeroRobot to add an action to the task list of
        the corresponding service

        @param action: action is the name of the action to add to the task list
        @param args: dictionnary of the argument to pass to the action
        """
        req = {
            "action_name": action,
        }
        if args:
            req["args"] = args

        try:
            task, _ = self._zrobot_client.api.services.AddTaskToList(req, service_guid=self.guid)
        except HTTPError as err:
            if err.response.status_code == 400:
                raise RuntimeError(err.response.json()['message'])
            raise err

        return _task_proxy_from_api(task, self)

    def delete(self):
        self._zrobot_client.api.services.DeleteService(self.guid)
        # clean up secret from zrobot client
        config_mgr.remove_secret(self._zrobot_client.instance, self.guid)


class TaskListProxyGedis:
    def __init__(self, service_proxy):
        self._service = service_proxy

    def _list_task(self, all=False):
        kwargs = {
            'secrets': self._service._http_client.config.data['secrets_'],
            'god_token': self._service._http_client.config.data['god_token_'],
            'guid': self._service.guid,
            'all': all,
        }
        schema = j.data.schema.get(url='zrobot.task')
        return list(map(lambda x: schema.get(capnpbin=x), self._service._gedis_client.services.tasks(**kwargs)))

    def empty(self):
        return len(self._list_task()) <= 0

    def list_tasks(self, all=False):
        tasks = self._list_task(all)
        return list(map(lambda x: _task_proxy_from_gedis(x, self._service), tasks))

    def get_task_by_guid(self, guid):
        """
        return a task from the list by it's guid
        """
        kwargs = {
            'secrets': self._service._http_client.config.data['secrets_'],
            'god_token': self._service._http_client.config.data['god_token_'],
            'guid': self._service.guid,
            'task_guid': guid,
        }
        return _task_proxy_from_gedis(self._service._gedis_client.services.task_get(**kwargs), self._service)


class TaskListProxy:

    def __init__(self, service_proxy):
        self._service = service_proxy

    def empty(self):
        tasks, _ = self._service._zrobot_client.api.services.getTaskList(
            service_guid=self._service.guid, query_params={'all': False})
        return len(tasks) <= 0

    def list_tasks(self, all=False):
        tasks, _ = self._service._zrobot_client.api.services.getTaskList(
            service_guid=self._service.guid, query_params={'all': all})
        return [_task_proxy_from_api(t, self._service) for t in tasks]

    def get_task_by_guid(self, guid):
        """
        return a task from the list by it's guid
        """
        try:
            task, _ = self._service._zrobot_client.api.services.GetTask(service_guid=self._service.guid, task_guid=guid)
            return _task_proxy_from_api(task, self._service)
        except HTTPError as err:
            if err.response.status_code == 404:
                raise TaskNotFoundError("no task with guid %s found" % guid)
            raise err


class TaskProxyGedis(Task):
    """
    class that represent a task on a remote service

    the state attribute is an property that do an API call to get the
    actual state of the task on the remote ZeroRobot
    """

    def __init__(self, guid, service, action_name, args, created):
        super().__init__(func=None, args=args)
        # since this is going to work over network, we increase the
        # sleep period to not overload the network
        self._sleep_period = 5
        self.action_name = action_name
        self.service = service
        self.guid = guid
        self._created = created

    def execute(self):
        raise RuntimeError("a TaskProxy should never be executed")

    def _get_task(self):
        kwargs = {
            'secrets': self.service._http_client.config.data['secrets_'],
            'god_token': self.service._http_client.config.data['god_token_'],
            'guid': self.service.guid,
            'task_guid': self.guid,
        }
        return self.service._gedis_client.services.task_get(**kwargs)

    @property
    def result(self):
        if self._result is None:
            task = self._get_task()
            if task.result:
                self._result = j.data.serializers.msgpack.loads(task.result)
        return self._result

    @property
    def duration(self):
        if self._duration is None:
            task = self._get_task()
            self._duration = task.duration
        return self._duration

    @property
    def state(self):
        task = self._get_task()
        return task.state

    @state.setter
    def state(self, value):
        logger.warning("you can't change the statet of a TaskProxy")
        return

    @property
    def eco(self):
        if self._eco is None:
            task = self._get_task()
            if task.eco.trace:
                self._eco = Eco.from_dict(task.eco._ddict)
        return self._eco

    def _cancel(self):
        # TODO:
        raise NotImplementedError()
        # self.service._zrobot_client.api.services.CancelTask(task_guid=self.guid, service_guid=self.service.guid)


class TaskProxy(Task):
    """
    class that represent a task on a remote service

    the state attribute is an property that do an API call to get the
    actual state of the task on the remote ZeroRobot
    """

    def __init__(self, guid, service, action_name, args, created):
        super().__init__(func=None, args=args)
        # since this is going to work over network, we increase the
        # sleep period to not overload the network
        self._sleep_period = 5
        self.action_name = action_name
        self.service = service
        self.guid = guid
        self._created = created

    def execute(self):
        raise RuntimeError("a TaskProxy should never be executed")

    @property
    def result(self):
        if self._result is None:
            task, _ = self.service._zrobot_client.api.services.GetTask(
                task_guid=self.guid, service_guid=self.service.guid)
            if task.result:
                self._result = j.data.serializers.json.loads(task.result)
        return self._result

    @property
    def duration(self):
        if self._duration is None:
            task, _ = self.service._zrobot_client.api.services.GetTask(
                task_guid=self.guid, service_guid=self.service.guid)
            self._duration = task.duration
        return self._duration

    @property
    def state(self):
        task, _ = self.service._zrobot_client.api.services.GetTask(task_guid=self.guid, service_guid=self.service.guid)
        return task.state.value

    @state.setter
    def state(self, value):
        logger.warning("you can't change the statet of a TaskProxy")
        return

    @property
    def eco(self):
        if self._eco is None:
            task, _ = self.service._zrobot_client.api.services.GetTask(
                task_guid=self.guid, service_guid=self.service.guid)
            if task.eco:
                self._eco = Eco.from_dict(task.eco.as_dict())
        return self._eco

    def _cancel(self):
        self.service._zrobot_client.api.services.CancelTask(task_guid=self.guid, service_guid=self.service.guid)


def _task_proxy_from_api(task, service):
    t = TaskProxy(task.guid, service, task.action_name, task.args, task.created)
    if task.duration:
        t._duration = task.duration

    if task.eco:
        t._eco = Eco.from_dict(task.eco.as_dict())

    return t


def _task_proxy_from_gedis(task, service):
    t = TaskProxyGedis(task.guid, service, task.action_name, {}, task.created)
    # t = TaskProxyGedis(task.guid, self, task.action_name, task.args, task.created) #TODO: uncomment when gedis support dict type
    if task.duration:
        t._duration = task.duration
    if task.eco.trace:
        t._eco = Eco.from_dict(task.eco._ddict)
    return t
