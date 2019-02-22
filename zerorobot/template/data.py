
import os

from jumpscale import j

from zerorobot.task import PRIORITY_SYSTEM


class ServiceData(dict):
    """
    Small wrapper around dict object to make
    access to capnp object easy for the service
    """

    def __init__(self, service, *args, **kwargs):
        """
        @param schema_path: path to the
        """
        super().__init__(*args, **kwargs)
        self._nacl = j.data.nacl.get()
        self._type_map = {}
        self._service = service
        path = os.path.join(service.template_dir, 'schema.capnp')
        if os.path.exists(path):
            schema_str = j.sal.fs.fileGetContents(path)
            msg = j.data.capnp.getObj(schema_str)
            self.update(msg.to_dict(verbose=True))

    def __setitem__(self, key, value):
        self._type_map[key] = type(value)
        if key[-1] == '_':
            value = self._nacl.encryptSymmetric(value)
        return super().__setitem__(key, value)

    def get_decrypted(self, key):
        value = self[key]
        value = self._nacl.decryptSymmetric(value)
        if self._type_map[key] == str:
            value = value.decode()
        return value

    def set_encrypted(self, key, value):
        self._type_map[key] = type(value)
        return super().__setitem__(key, self._nacl.encryptSymmetric(value))

    def update_secure(self, data):
        """
        @param data: dict of data to be merge with current one

        this method call update_data on the service
        update_data can be overwritten by the creator of the service
        """
        if data is None:
            data = {}

        if not isinstance(data, dict):
            raise ValueError('argument should be a dict not %s' % type(data))

        if data == {}:
            return
        # schedule the update of the data. This is required to serialize data access
        return self._service._schedule_action(action='update_data', args={'data': data}, priority=PRIORITY_SYSTEM)

    def save(self, path):
        """
        Serialize the data into a file

        @param path: file path where to save the data
        """
        j.data.serializer.yaml.dump(path, dict(self))

    def load(self, path):
        """
        Load the data from a file created by the save method

        @param path: file path from where to load the data
        """
        self.update(j.data.serializer.yaml.load(path))
