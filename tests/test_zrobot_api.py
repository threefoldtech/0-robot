import os
import shutil
import tempfile
import time
import unittest
import uuid
from multiprocessing import Process

from gevent import monkey
from js9 import j
from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol
from zerorobot.dsl.ZeroRobotAPI import TemplateNotFoundError, ZeroRobotAPI
from zerorobot.robot import Robot
from zerorobot.service_proxy import ServiceProxy
from zerorobot.template.base import TemplateBase

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


class TestZRobotAPI(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName=methodName)
        self.api = None

    def _start_robot(self, id, with_tmpl=False):
        def new(id, with_tmpl):
            robot = Robot()
            robot._data_dir = tempfile.mkdtemp(prefix="robot1")
            if with_tmpl:
                robot.add_template_repo('http://github.com/jumpscale/0-robot', directory='tests/fixtures/templates')

            listen = "localhost:660%d" % int(id)
            addr = "http://%s" % listen
            robot.start(listen=listen)
            # return robot

        addr = "http://localhost:660%d" % int(id)
        p = Process(target=new, args=(id, with_tmpl))
        p.start()
        return p, addr

    def setUp(self):
        self.api = ZeroRobotAPI()
        self.ps = []
        self.instances = []

        # start 2 robots
        for i in range(2):
            p, addr = self._start_robot(i, with_tmpl=True)
            self.ps.append(p)
            instance = j.data.hash.md5_string(addr)
            self.api._config_mgr.set(instance, addr)
            self.instances.append(instance)

        # give time to the robot to starts TODO: find better then sleep
        time.sleep(1)

        # make sure we don't have any service loaded
        scol._guid_index = {}
        scol._name_index = {}
        # make sure we don't have any template loaded
        tcol._templates = {}

    def tearDown(self):
        for p in self.ps:
            p.terminate()
            p.join()

        for instance in self.instances:
            self.api._config_mgr.delete(instance)
        # TODO: cleanup data_dir of each robots

        # make sure we don't have any service loaded
        scol._guid_index = {}
        scol._name_index = {}
        # make sure we don't have any template loaded
        tcol._templates = {}

    def test_robots_discovery(self):
        self.assertGreaterEqual(len(self.api.robots), 2, "should have discovered at least the 2 robots that are running for the test")
        for addr in self.instances:
            self.assertIn(addr, self.api.robots.keys())

    def test_service_create(self):
        with self.assertRaises(TemplateNotFoundError, msg='trying to create a service from non exiting template should raise '):
            self.api.services.create("github.com/jumpscale/0-robot/notexists/0.0.1", 'node1')

        # make sure we don't have any template loaded in the current process
        tcol._templates = {}
        node1 = self.api.services.create("github.com/jumpscale/0-robot/node/0.0.1", 'node1')
        # since we don't have any template in current process, we force to use a another robot, so it's a remote service
        # that is created
        self.assertEqual(type(node1), ServiceProxy)

        # load template in current process
        tcol.add_repo('http://github.com/jumpscale/0-robot', directory='tests/fixtures/templates')
        # now that we have some templates loaded, it should create a local service
        node2 = self.api.services.create("github.com/jumpscale/0-robot/node/0.0.1", 'node2')
        self.assertTrue(isinstance(node2, TemplateBase))

        # the api should get all services from both local and remote robots
        self.assertEqual(len(self.api.services.names), 2)
        self.assertEqual(len(self.api.services.guids), 2)

    def test_service_search(self):
        node1 = self.api.services.create("github.com/jumpscale/0-robot/node/0.0.1", 'node1')
        node2 = self.api.services.create("github.com/jumpscale/0-robot/node/0.0.1", 'node2')
        vm1 = self.api.services.create("github.com/jumpscale/0-robot/vm/0.0.1", 'vm1')

        results = self.api.services.search("github.com/jumpscale/0-robot/node/0.0.1")
        self.assertEqual(len(results), 2)
        guids = [node1.guid, node2.guid]
        for s in results:
            self.assertIn(s.guid, guids)
