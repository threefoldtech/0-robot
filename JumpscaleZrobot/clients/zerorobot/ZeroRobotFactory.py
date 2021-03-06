import collections
import os

from jumpscale import j
from zerorobot.dsl.ZeroRobotManager import ZeroRobotManager

from .ZeroRobotClient import ZeroRobotClient

JSConfigFactoryBase = j.tools.configmanager.base_class_configs


class ZeroRobotFactory(JSConfigFactoryBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.zrobot"
        super().__init__(child_class=ZeroRobotClient)
        self._robots = RobotLoader()

    def generate(self):
        """
        generate the client out of the raml specs
        """
        path = j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")
        c = j.tools.raml.get(path)
        # c.specs_get('https://github.com/Jumpscale/0-robot/blob/master/raml')
        c.client_python_generate()

    @property
    def robots(self):
        """
        list all the ZeroRobot accessible
        return a dictionary with
        key = instance name of the 0-robot
        value: ZeroRobotManager object

        ZeroRobotManager is a high level client for 0-robot that present the 0-robot API with an easy interface
        see https://zero-os.github.io/0-robot/api/zerorobot/dsl/ZeroRobotManager.m.html for full API documentation
        """
        return self._robots

    def get_by_id(self, node_id):
        directory = j.clients.threefold_directory.get()
        node, resp = directory.api.GetCapacity(node_id)
        resp.raise_for_status()
        client = self.get(node_id)
        if client.config.data['url'] != node.robot_address:
            client.config.data_set('url', node.robot_address)
            client.config.save()
        return self.robots[node_id]


class RobotLoader(collections.MutableMapping):

    def __call__(self, key, **kwargs):
        return self.get(key, **kwargs)

    def __getitem__(self, key, **kwargs):
        return self.get(key, **kwargs)

    def __setitem__(self, key, value):
        raise NotImplementedError("you cannot set a robot.")

    def __delitem__(self, key):
        j.clients.zrobot.delete(key)

    def __iter__(self):
        return iter(j.clients.zrobot.getall())

    def __len__(self):
        return j.clients.zrobot.count()

    def __keytransform__(self, key):
        return key

    def get(self, key, **kwargs):
        if not isinstance(key, str):
            raise TypeError

        j.clients.zrobot.get(key, **kwargs)

        return ZeroRobotManager(key)

    def __repr__(self):
        robots = {instance: "ZeroRobotManager" for instance in j.clients.zrobot.list()}
        return str(robots)

    __str__ = __repr__
