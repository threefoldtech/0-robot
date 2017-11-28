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
            self.assertEqual(err.args[0], "service with name=nan not found")

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

    def test_list_services(self):
        services = scol.list_services()
        self.assertEqual(len(services), 0, "services count should be 0")

        s1 = FakeService('1111', 's1')
        s2 = FakeService('2222', 's2')
        s3 = FakeService('3333', 's3')
        scol.add_service(s1)
        scol.add_service(s2)

        services = scol.list_services()
        self.assertEqual(len(services), 2, "services count should be 2")
        self.assertIn(s1, services, 'service s1 should be in the returned service list')
        self.assertIn(s2, services, 'service s2 should be in the returned service list')
        self.assertNotIn(s3, services, 'service s3 should not be in the returned service list')
