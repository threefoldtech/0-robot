import os
import shutil
import unittest
import uuid

from zerorobot.robot import Robot
from zerorobot.dsl.ZeroRobotClient import ZeroRobotClient
from zerorobot.service_proxy import ServiceProxy
from gevent import monkey

from zerorobot import template_collection as tcol
from zerorobot import service_collection as scol
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


class TestServiceProxy(unittest.TestCase):

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

    def _create_proxy(self):
        template = 'github.com/jumpscale/zerorobot/node/0.0.1'
        name = 'node1'
        proxy = self.cl.services.create(template, name)
        service = scol.get_by_guid(proxy.guid)
        return (proxy, service)

    def test_create_proxy(self):
        proxy, service = self._create_proxy()

        self.assertEqual(proxy.guid, service.guid, "proxy should have same guid as real service")
        self.assertEqual(proxy.name, service.name, "proxy should have same name as real service")
        self.assertIsNone(proxy.data, "proxy should not have access to the data of the services")

    def test_state(self):
        proxy, service = self._create_proxy()

        service.state.set('foo', 'bar', 'ok')
        self.assertDictEqual(service.state.categories, proxy.state.categories, "proxy state should reflect service state")

        service.state.set('foo', 'bar', 'error')
        self.assertEqual(proxy.state.get('foo', 'bar'), {'bar': 'error'}, 'update of service state, should be reflect in proxy')

        proxy.state.set('foo', 'bar', 'ok')
        self.assertNotEqual(service.state.get('foo', 'bar'), {'bar': 'ok'}, 'update of proxy state, should not be reflect in service')

    def test_task_list(self):
        proxy, service = self._create_proxy()

        task = service.schedule_action('start')

        self.assertEqual(len(proxy.task_list.list_tasks(all=True)), 1, "task create on service should be visible from the proxy")
        proxy_task = proxy.task_list.get_task_by_guid(task.guid)
        self.assertEqual(proxy_task.state, task.state, "state of a task should be reflect on the proxy task")
        task.state = 'error'
        self.assertEqual(proxy_task.state, task.state, "state of a task should be reflect on the proxy task")

        proxy.schedule_action('stop')
        self.assertEqual(len(service.task_list.list_tasks(all=True)), 2, "task create on proxy should be visible on real service")

    def test_delete(self):
        proxy, service = self._create_proxy()

        proxy.delete()
        with self.assertRaises(KeyError, msg='deleting a proxy, should delete the real service'):
            scol.get_by_guid(proxy.guid)
