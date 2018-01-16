
import os

from js9 import j

from zerorobot.task import PRIORITY_SYSTEM


class ServiceData(dict):
    """
    Small wrapper around dict object to make
    access to capnp object easy for the service
    """

    def __init__(self, service):
        """
        @param schema_path: path to the
        """
        self._service = service
        path = os.path.join(service.template_dir, 'schema.capnp')
        if os.path.exists(path):
            schema_str = j.sal.fs.fileGetContents(path)
            msg = j.data.capnp.getObj(schema_str)
            self.update(msg.to_dict(verbose=True))

    def update_secure(self, d):
        """
        @param d: dict of data to be merge with current one

        this method call update_data on the service
        update_data can be overwritten by the creator of the service
        """
        if not isinstance(d, dict):
            raise ValueError('argument should be a dict not %s' % type(d))

        if d == {}:
            return
        # schedule the update of the data. This is required to serialize data access
        self._service._schedule_action('update_data', {'d': d}, None, PRIORITY_SYSTEM)

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
