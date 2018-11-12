import unittest
from random import random
import time

import gevent

from jumpscale import j

from zerorobot.dsl.config_mgr import ConfigMgr


class TestConfigMgr(unittest.TestCase):

    def setUp(self):
        self.instance = j.data.idgenerator.generateGUID()
        self.mgr = ConfigMgr()

    def tearDown(self):
        self.mgr.delete(self.instance)

    def test_config_mgr(self):

        url = 'http://localhost:6600'
        robot = self.mgr.get(self.instance, url)

        assert self.instance in self.mgr.list()
        assert robot is not None
        assert robot._client.config.data['url'] == url

        self.mgr.delete(self.instance)
        assert self.instance not in self.mgr.list()

    def test_config_mgr_append_secret(self):
        mgr = ConfigMgr()
        self.instance = j.data.idgenerator.generateGUID()
        url = 'http://localhost:6600'
        robot = self.mgr.get(self.instance, url)

        self.mgr.append_secret(self.instance, 'secret1')
        self.mgr.append_secret(self.instance, 'secret2')

        robot = self.mgr.get(self.instance)
        assert robot._client.config.data['secrets_'] == ['secret1', 'secret2']

        self.mgr.delete(self.instance)
        assert self.instance not in self.mgr.list()

    def test_concurrent(self):
        def test():
            instance = j.data.idgenerator.generateGUID()
            url = 'http://localhost:6600'
            print('create %s' % instance)
            robot = self.mgr.get(instance, url)

            assert instance in self.mgr.list()
            assert robot is not None
            assert robot._client.config.data['url'] == url

            for i in range(10):
                print('append secret to %s' % instance)
                time.sleep(random())
                self.mgr.append_secret(instance, 'secret%d' % i)

            robot = self.mgr.get(instance)
            assert len(robot._client.config.data['secrets_']) == 10

            print('delete %s' % instance)
            self.mgr.delete(instance)
            assert instance not in self.mgr.list()

        gls = []
        for _ in range(400):
            gls.append(gevent.spawn(test))

        gevent.joinall(gls, raise_error=True)
