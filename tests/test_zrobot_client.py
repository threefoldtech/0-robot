import os
import shutil
import unittest
import uuid

from gevent import pool
from jumpscale import j
from zerorobot import config
from zerorobot import service_collection as scol
from zerorobot.dsl.ZeroRobotManager import (TemplateNotFoundError,
                                            ZeroRobotManager)
from zerorobot.robot import Robot
from zerorobot.service_proxy import ServiceProxy


class TestZRobotClient(unittest.TestCase):

    def setUp(self):
        j.clients.zrobot.get('test', {'url': 'http://localhost:6600'})
        self.cl = ZeroRobotManager('test')
        self.robot = Robot()
        self.robot.set_data_repo(j.sal.fs.getTmpDirPath())
        self.robot.add_template_repo('http://github.com/threefoldtech/0-robot', directory='tests/fixtures/templates')
        if os.path.exists(config.data_repo.path):
            shutil.rmtree(config.data_repo.path)
        # make sure we don't have any service loaded
        scol.drop_all()
        self.robot.start(listen='127.0.0.1:6600', block=False, testing=True)

    def tearDown(self):
        self.robot.stop(timeout=0)
        if os.path.exists(config.data_repo.path):
            shutil.rmtree(config.data_repo.path)
        # make sure we don't have any service loaded
        scol.drop_all()
        j.clients.zrobot.delete('test')

    def test_list_templates(self):
        uids = [str(x) for x in self.cl.templates.uids]
        self.assertEqual(len(uids), 6, "number of templates should be 6")
        self.assertIn('github.com/threefoldtech/0-robot/node/0.0.1', uids)
        self.assertIn('github.com/threefoldtech/0-robot/vm/0.0.1', uids)

    def test_service_create(self):
        with self.assertRaises(TemplateNotFoundError, msg='TemplateNotFoundError should be raise\
                                                        if trying to create service from a non existing template'):
            self.cl.services.create('github.com/threefoldtech/0-robot/notexits/0.0.1', 'foo')

        data = {'ip': '127.0.0.1'}
        node = self.cl.services.create('github.com/threefoldtech/0-robot/node/0.0.1', 'node1', data)
        self.assertEqual(type(node), ServiceProxy, 'service type should be ServiceProxy')
        # ensure the services actually exists
        scol.get_by_name(node.name)
        node = scol.get_by_guid(node.guid)
        self.assertEqual(node.data['ip'], data['ip'], "data send during creation of the service should be set to the actual service")

        self.assertEqual(len(self.cl.services.names), 1, "listing of service per name should return 1")
        self.assertEqual(len(self.cl.services.guids), 1, "listing of service per guid should return 1")

    def test_service_create_without_name(self):
        data = {'ip': '127.0.0.1'}
        node = self.cl.services.create('github.com/threefoldtech/0-robot/node/0.0.1', data=data)
        self.assertEqual(type(node), ServiceProxy, 'service type should be ServiceProxy')
        self.assertEqual(node.name, node.guid, "service name should be equal to service guid when created without name")
