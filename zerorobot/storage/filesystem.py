import os
import shutil

from jumpscale import j

from .base import ServiceStorageBase, _serialize_service


class FileSystemServiceStorage(ServiceStorageBase):

    def __init__(self, path):
        super().__init__()
        self._root = path
        if not os.path.exists(path):
            os.makedirs(path)

    def _service_path(self, service):
        return os.path.join(
            self._root,
            service.template_uid.host,
            service.template_uid.account,
            service.template_uid.repo,
            service.template_uid.name,
            service.name,
            service.guid
        )

    def save(self, service):
        path = self._service_path(service)
        if not os.path.exists(path):
            os.makedirs(path)

        service_path = os.path.join(path, 'service.yaml.tmp')
        state_path = os.path.join(path, 'state.yaml.tmp')
        data_path = os.path.join(path, 'data.yaml.tmp')
        task_path = os.path.join(path, 'tasks.yaml.tmp')

        serialized_service = _serialize_service(service)
        j.data.serializer.yaml.dump(service_path, serialized_service['service'])
        j.data.serializer.yaml.dump(state_path, serialized_service['states'])
        j.data.serializer.yaml.dump(data_path, serialized_service['data'])
        j.data.serializer.yaml.dump(task_path, serialized_service['tasks'])

        j.sal.fs.moveFile(service_path, service_path[:-4])
        j.sal.fs.moveFile(state_path, state_path[:-4])
        j.sal.fs.moveFile(data_path, data_path[:-4])
        j.sal.fs.moveFile(task_path, task_path[:-4])

    def list(self):
        for service_dir in j.sal.fs.listDirsInDir(self._root, recursive=True):
            info_path = os.path.join(service_dir, 'service.yaml')
            if not os.path.exists(info_path):
                continue

            info_data = j.data.serializer.yaml.load(info_path)
            state_data = j.data.serializer.yaml.load(os.path.join(service_dir, 'state.yaml'))
            data_data = j.data.serializer.yaml.load(os.path.join(service_dir, 'data.yaml'))
            tasks_data = j.data.serializer.yaml.load(os.path.join(service_dir, 'tasks.yaml'))

            yield {
                'service': info_data,
                'states': state_data,
                'data': data_data,
                'tasks': tasks_data,
            }

    def delete(self, service):
        path = self._service_path(service)
        if path and os.path.exists(path):
            shutil.rmtree(os.path.dirname(path))

    def health(self):
        try:
            file_path = os.path.join(self._root, 'healthcheck.tmp')
            with open(file_path, 'wb+') as f:
                f.write(os.urandom(4 * 1024))
            os.remove(file_path)
            return True
        except:
            return False
