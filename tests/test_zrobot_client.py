
import os
import shutil
import unittest
import uuid

from gevent import monkey
from zerorobot import service_collection as scol
from zerorobot.dsl.ZeroRobotClient import ZeroRobotClient, TemplateNotFoundError
from zerorobot.robot import Robot
from zerorobot.service_proxy import ServiceProxy

# need to patch sockets to make requests async
monkey.patch_all(
    socket=True,
    dns=True,
    time=True,
    select=True,
    thread=True,
    os=True,
    ssl=True,
    httplib=False,
    subprocess=False,
    sys=False,
    aggressive=True,
    Event=False,
    builtins=True,
    signal=True)


class TestZRobotClient(unittest.TestCase):

    def setUp(self):
        self.cl = ZeroRobotClient('http://localhost:6600')
        self.robot = Robot()
        self.robot.set_data_repo('http://github.com/jumpscale/zerorobot')
        self.robot.add_template_repo('http://github.com/jumpscale/zerorobot', directory='tests/fixtures/templates')
        if os.path.exists(self.robot._data_dir):
            shutil.rmtree(self.robot._data_dir)
        # make sure we don't have any service loaded
        scol._guid_index = {}
        scol._name_index = {}
        self.robot.start(block=False)

    def tearDown(self):
        self.robot.stop()
        shutil.rmtree(self.robot._data_dir)

    def test_list_templates(self):
        uids = self.cl.templates.uids

        self.assertEqual(len(uids), 2, "number of templates should be 2")
        self.assertIn('github.com/jumpscale/zerorobot/node/0.0.1', uids)
        self.assertIn('github.com/jumpscale/zerorobot/vm/0.0.1', uids)

    def test_service_create(self):
        with self.assertRaises(TemplateNotFoundError, msg='TemplateNotFoundError should be raise\
                                                        if trying to create service from a non existing template'):
            self.cl.services.create('github.com/jumpscale/zerorobot/notexits/0.0.1', 'foo')

        data = {'ip': '127.0.0.1'}
        node = self.cl.services.create('github.com/jumpscale/zerorobot/node/0.0.1', 'node1', data)
        self.assertEqual(type(node), ServiceProxy, 'service type should be ServiceProxy')
        # ensure the services actually exists
        scol.get_by_name(node.name)
        node = scol.get_by_guid(node.guid)
        self.assertEqual(node.data['ip'], data['ip'], "data send during creation of the service should be set to the actual service")

        self.assertEqual(len(self.cl.services.names), 1, "listing of service per name should return 1")
        self.assertEqual(len(self.cl.services.guids), 1, "listing of service per guid should return 1")
