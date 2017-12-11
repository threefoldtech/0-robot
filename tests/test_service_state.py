import os
import tempfile
import unittest

from js9 import j

from zerorobot.template.template import ServiceState, BadServiceStateError, StateCategoryNotExistsError, StateCheckError


class TestServiceState(unittest.TestCase):

    def test_create_state(self):
        state = ServiceState()
        self.assertIsNotNone(state.categories, "categories dictionnary should not be None")

    def test_set_state(self):
        state = ServiceState()
        state.set('network', 'tcp-80', 'ok')
        state.set('network', 'tcp-81', 'error')

        self.assertEqual(state.categories['network']['tcp-80'], 'ok', "state should be ok")
        self.assertEqual(state.categories['network']['tcp-81'], 'error', "state should be error")

        with self.assertRaises(BadServiceStateError, msg="support state should only be 'ok' or 'error'"):
            state.set('network', 'tcp-80', 'other')

    def test_get_state(self):
        state = ServiceState()
        state.set('network', 'tcp-80', 'ok')
        state.set('network', 'tcp-81', 'error')

        self.assertDictEqual(state.get('network'), {'tcp-80': 'ok', 'tcp-81': 'error'})
        self.assertDictEqual(state.get('network', 'tcp-80'), {'tcp-80': 'ok'})

        with self.assertRaises(StateCategoryNotExistsError, msg='category should not exists'):
            state.get('foo')

        with self.assertRaises(StateCategoryNotExistsError, msg='tag should not exists'):
            # also when trying to get tag that doesn't exists
            state.get('network', 'foo')

    def test_repr(self):
        state = ServiceState()
        state.set('network', 'tcp-80', 'ok')
        state.set('network', 'tcp-81', 'error')
        self.assertEqual(str(state), str({'network': {'tcp-80': 'ok', 'tcp-81': 'error'}}))

    def test_save_load(self):
        state = ServiceState()
        state.set('network', 'tcp-80', 'ok')
        state.set('network', 'tcp-81', 'error')

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'zrobot-test-state.yml')
            state.save(path)

            with open(path) as f:
                content = f.read()
            self.assertEqual(content, j.data.serializer.yaml.dumps(state.categories))

            state2 = ServiceState()
            state2.load(path)
            self.assertDictEqual(state.categories, state2.categories)

    def test_check(self):
        state = ServiceState()
        state.set('network', 'tcp-80', 'ok')

        self.assertTrue(state.check('network', 'tcp-80', 'ok'))
        with self.assertRaises(StateCheckError):
            self.assertFalse(state.check('network', 'tcp-80', 'error'))
        with self.assertRaises(StateCheckError):
            self.assertFalse(state.check('network', '', 'ok'))
        with self.assertRaises(StateCheckError):
            self.assertFalse(state.check('foo', 'tcp-80', 'ok'))
        with self.assertRaises(StateCheckError):
            self.assertFalse(state.check('', '', 'ok'))
        with self.assertRaises(StateCheckError):
            self.assertFalse(state.check(None, 'tcp-80', 'ok'))
        with self.assertRaises(StateCheckError):
            self.assertFalse(state.check('network', None, 'ok'))
