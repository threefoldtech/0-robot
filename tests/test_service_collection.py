import unittest
from zerorobot import service_collection as scol


class FakeService:

    def __init__(self, guid, name):
        self.name = name
        self.guid = guid


class TestServiceCollection(unittest.TestCase):

    def tearDown(self):
        scol._name_index = {}
        scol._guid_index = {}

    def test_add_get_service(self):
        service = FakeService('1234567890', 's1')
        scol.add_service(service)

        self.assertEqual(service, scol.get_by_guid('1234567890'))
        self.assertEqual(service, scol.get_by_name('s1'))
        try:
            scol.get_by_name("nan")
        except KeyError as err:
            self.assertEqual(err.args[0], "service nan not found")

    def test_service_overwrite(self):
        s1 = FakeService('1111', 's1')
        s2 = FakeService('1111', 's2')
        s3 = FakeService('2222', 's1')
        scol.add_service(s1)

        try:
            scol.add_service(s2)
            scol.add_service(s3)
            self.fail('should raise exception is try to overwrite service')
        except scol.ServiceConflictError as err:
            pass
