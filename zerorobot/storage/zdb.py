import os

import msgpack

from jumpscale import j

from .base import ServiceStorageBase, _serialize_service

logger = j.logger.get(__name__)

_service_prefix = "service_"
_tasklist_prefix = "tasklist_"
_data_prefix = "data_"
_state_prefix = "state_"


class ZDBServiceStorage(ServiceStorageBase):

    def __init__(self, addr, port, namespace=None, admin_passwd=''):
        super().__init__()
        if not namespace:
            namespace = 'zrobot_data'
        self._client = j.clients.zdb.configure(instance='zrobot',
                                               secrets='',
                                               addr=addr,
                                               port=port,
                                               adminsecret=admin_passwd or '',
                                               mode='user')

        self._ns = self._client.zdb.namespace_new(namespace)

    def save(self, service):
        logger.info("save %s to 0-db backend", service.guid)
        serialized_service = _serialize_service(service)
        logger.debug(serialized_service)
        self._ns.set(msgpack.dumps(serialized_service['service']), _service_prefix+service.guid)
        self._ns.set(msgpack.dumps(serialized_service['tasks']), _tasklist_prefix+service.guid)
        self._ns.set(msgpack.dumps(serialized_service['data']), _data_prefix+service.guid)
        self._ns.set(msgpack.dumps(serialized_service['states']), _state_prefix+service.guid)

    def list(self):
        logger.info("list services from 0-db backend")
        for key in self._ns.list():
            # since we also save webhooks info into the same namespace
            if not key.startswith(_service_prefix.encode()):
                continue

            guid = key[len(_service_prefix):].decode()

            service_bin = self._ns.get(key)
            tasklist_bin = self._ns.get((_tasklist_prefix+guid).encode())
            data_bin = self._ns.get((_data_prefix+guid).encode())
            state_bin = self._ns.get((_state_prefix+guid).encode())

            service = msgpack.loads(service_bin, encoding='utf-8')
            tasklist = msgpack.loads(tasklist_bin, encoding='utf-8')
            data = msgpack.loads(data_bin, encoding='utf-8')
            state = msgpack.loads(state_bin, encoding='utf-8')

            logger.info("service %s loaded" % service['guid'])
            yield {
                'service': service,
                'tasks': tasklist,
                'data': data,
                'states': state,
            }

    def delete(self, service):
        logger.info("delete %s from 0-db backend", service.guid)
        self._ns.delete(_service_prefix+service.guid)
        self._ns.delete(_tasklist_prefix+service.guid)
        self._ns.delete(_data_prefix+service.guid)
        self._ns.delete(_state_prefix+service.guid)

    def health(self):
        try:
            ns_name = 'healthcheck'
            ns = self._client.zdb.namespace_new(ns_name)
            self._client.zdb.namespace_delete(ns_name)
            return True
        except:
            return False
