
import os

from js9 import j


class ServiceData(dict):
    """
    Small wrapper around dict object to make
    access to capnp object easy for the service
    """

    def __init__(self, service):
        """
        @param schema_path: path to the
        """
        path = os.path.join(service.template_dir, 'schema.capnp')
        if os.path.exists(path):
            schema_str = j.sal.fs.fileGetContents(path)
            msg = j.data.capnp.getObj(schema_str)
            self.update(msg.to_dict(verbose=True))

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
