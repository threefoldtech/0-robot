import os
import tempfile
import unittest

from js9 import j
from zerorobot.template.base import (ActionNotFoundError,
                                     BadActionArgumentError, BadTemplateError,
                                     TemplateBase)
from zerorobot.template_collection import _load_template


class TestServiceData(unittest.TestCase):

    def load_template(self, name):
        """
        name of the template to load from the
        fixtures/templates folder
        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return _load_template(os.path.join(dir_path, 'fixtures', 'templates', name))

    def test_instanciate_service(self):
        self.skipTest("not implemented yet")
        # Node = self.load_template('node')
        # srv = Node('testnode')
        # self.assertIsNotNone(srv.data, "service data should not be None")

        # srv.data.ip = '127.0.0.1'
        # srv.data.port = 12
        # srv.data.list = [1, 2, 3]

        # self.assertEqual(srv.data.ip, srv.data._data['ip'], "attribute on data class should be the same as in capnp object")
        # self.assertEqual(srv.data.port, srv.data._data['port'], "attribute on data class should be the same as in capnp object")
        # self.assertEqual(srv.data.list, srv.data._data['list'], "attribute on data class should be the same as in capnp object")

        # srv.data.list.append(4)
        # self.assertEqual(len(srv.data.list), 4, "append should work on list")
        # srv.data.list.pop()
        # self.assertEqual(len(srv.data.list), 3, "pop should work on list")
