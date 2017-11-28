import unittest
import os

from zerorobot import template_collection as tcol


class TestTemplateCollection(unittest.TestCase):

    def tearDown(self):
        tcol._templates = {}

    def test_load_template(self):
        # valid template
        file_path = os.path.join(os.path.dirname(__file__), 'fixtures/templates/node')
        tcol._load_template(file_path)
        self.assertEqual(len(tcol._templates), 1, 'should have loaded a template')

        # non existing template
        try:
            tcol._load_template("/not/existing/path")
            self.fail('loading non existing template should fail')
        except:
            pass

    def test_get_template(self):
        file_path = os.path.join(os.path.dirname(__file__), 'fixtures/templates/node')
        tcol._load_template(file_path)
        self.assertEqual(len(tcol._templates), 1, 'should have loaded a template')

        template = tcol.get_template('node')
        self.assertTrue(template is not None)

        try:
            tcol.get_template('notexist')
            self.fail("should raise KeyError")
        except KeyError:
            pass
