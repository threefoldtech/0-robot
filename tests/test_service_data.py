from zerorobot.template.data import ServiceData
from jumpscale import j
import pytest
import unittest


@pytest.fixture
def service():
    class Service():
        def __init__(self):
            self.template_dir = '/tmp'
    return Service()


def test_create_data(service):
    data = ServiceData(service)
    assert data is not None
    assert data._nacl is not None
    assert data._service == service


def test_data_encryption(service):
    data = ServiceData(service)
    data['foo'] = 'bar'
    data['foo_'] = 'bar'
    data['foo2_'] = b'bar'
    assert data['foo'] == 'bar'
    assert data['foo_'] != 'bar'
    assert data['foo2_'] != b'bar'
    assert data.get_decrypted('foo_') == 'bar'
    assert data.get_decrypted('foo2_') == b'bar'
    data.set_encrypted('foo3', 'bar')
    assert data['foo3'] != 'bar'
    assert data.get_decrypted('foo3') == 'bar'


def test_data_update(service):
    data = ServiceData(service)
    data.update({'foo': 'bar'})
    assert 'foo' in data._type_map
    assert data == {'foo': 'bar'}

    data.update({'foo_': 'bar'})
    data['foo_'] != 'bar'
    data.get_decrypted('foo_') == 'bar'
