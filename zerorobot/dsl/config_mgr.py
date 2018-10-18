
from gevent.queue import Queue
import gevent
from jumpscale import j

from jose import jwt

logger = j.logger.get(__name__)


class ConfigMgr():
    """
    Small class that abstract configmanager
    """

    def __init__(self):
        j.tools.configmanager.interactive = False
        self._queue = Queue()
        self._worker_gl = gevent.spawn(self._worker)

    def _worker(self):
        while True:
            func, args, resp_q = self._queue.get()
            try:
                if args:
                    result = func(*args)
                else:
                    result = func()
                resp_q.put(result)
            except Exception as err:
                logger.error("error in config manager %s" % err)
                resp_q.put(err)
                continue

    def _send_cmd(self, func, args):
        resp_q = Queue(maxsize=1)
        self._queue.put((func, args, resp_q))
        resp = resp_q.get()
        if isinstance(resp, Exception):
            raise resp
        return resp

    def _list(self):
        return j.clients.zrobot.list()

    def _get(self, instance, base_url=None):

        client = j.clients.zrobot.get(instance, interactive=False)
        if base_url and base_url != client.config.data['url']:
            client.config.data_set('url', base_url)
            client.config.save()
        return j.clients.zrobot.robots(instance)

    def _delete(self, instance):
        if not instance or not j.clients.zrobot.exists(instance):
            return
        j.clients.zrobot.delete(instance)

    def _append_secret(self, instance, secret):
        robot = self._get(instance)
        client = robot._client
        secrets = client.config.data['secrets_']
        if secret not in secrets:
            secrets.append(secret)
            client.config.data_set('secrets_', secrets)
            client.config.save()
        return client

    def _remove_secret(self, instance, service_guid):
        robot = self._get(instance)
        client = robot._client
        secrets = client.config.data['secrets_']
        for secret in list(secrets):
            try:
                claims = jwt.get_unverified_claims(secret)
            except:
                continue
            else:
                if claims.get('service_guid') == service_guid and secret in secrets:
                    secrets.remove(secret)
                    break

        client.config.data_set('secrets_', secrets)
        client.config.save()
        return client

    def get(self, instance, base_url=None):
        """
        get a 0-robot client

        if base_url is set and the current url in the config
        is different, base_url is used to replace the current configured url

        @param instance: instance name
        @param base_url: base_url of the client
        """
        return self._send_cmd(self._get, [instance, base_url])

    def list(self):
        """
        list all the available zerorobot client configured

        @return: a list of instance name
        """
        return self._send_cmd(self._list, None)

    def delete(self, instance):
        """
        deletes a config

        @param instance: instance name
        """
        return self._send_cmd(self._delete, instance)

    def append_secret(self, instance, secret):
        return self._send_cmd(self._append_secret, [instance, secret])

    def remove_secret(self, instance, service_guid):
        return self._send_cmd(self._remove_secret, [instance, service_guid])
