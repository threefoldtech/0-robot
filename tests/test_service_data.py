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
    assert data['foo'] == 'bar'
    data.set_encrypted('foo_', 'bar')
    data.set_encrypted('foo2_', b'bar')
    assert data.get_decrypted('foo_').decode() == 'bar'
    assert data.get_decrypted('foo2_') == b'bar'
    data.set_encrypted('foo3', 'bar')
    assert data['foo3'] != 'bar'
    assert data.get_decrypted('foo3').decode() == 'bar'

    # ensure trying decrypt clear data raises
    with pytest.raises(Exception):
        data.get_decrypted("foo")