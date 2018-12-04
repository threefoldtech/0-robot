import os

import msgpack

from jumpscale import j

from .base import ServiceStorageBase, _serialize_service


class ZDBServiceStorage(ServiceStorageBase):

    def __init__(self, addr, port, namespace=None, admin_passwd=''):
        super().__init__()
        self._key_prefix = 'service_'
        if not namespace:
            namespace = 'zrobot_data'
        self._client = j.clients.zdb.configure(instance='zrobot',
                                               secrets='',
                                               addr=addr,
                                               port=port,
                                               adminsecret=admin_passwd or '',
                                               mode='user')

        self._ns = self._client.zdb.namespace_new(namespace)

    def _service_key(self, service):
        return "service_%s" % service.guid

    def save(self, service):
        serialized_service = _serialize_service(service)
        self._ns.set(msgpack.dumps(serialized_service), self._key_prefix+service.guid)

    def list(self):
        for guid in self._ns.list():
            # since we also save webhooks info into the same namespace
            if not guid.startswith(self._key_prefix.encode()):
                continue

            obj = self._ns.get(guid)
            service = msgpack.loads(obj, encoding='utf-8')
            yield service

    def delete(self, service):
        self._ns.delete(self._key_prefix+service.guid)

    def health(self):
        try:
            ns_name = 'healthcheck'
            ns = self._client.zdb.namespace_new(ns_name)
            self._client.zdb.namespace_delete(ns_name)
            return True
        except:
            return False
