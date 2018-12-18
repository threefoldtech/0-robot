from .filesystem import FileSystemServiceStorage
from .zdb import ZDBServiceStorage

_store = None


def init(config):
    global _store
    data_repo = config.data_repo
    if data_repo.type == 'fs':
        _store = FileSystemServiceStorage(data_repo.path)
    elif data_repo.type == 'zdb':
        _store = ZDBServiceStorage(addr=data_repo.hostname,
                                   port=data_repo.port,
                                   namespace=data_repo.namespace,
                                   admin_passwd=data_repo.username)
    else:
        raise RuntimeError("unsupported storage type for service %s", data_repo.type)

    return _store


def save(service):
    if not _store:
        raise RuntimeError("storage has not be initialized")
    return _store.save(service)


def list():
    if not _store:
        raise RuntimeError("storage has not be initialized")
    return _store.list()


def delete(service):
    if not _store:
        raise RuntimeError("storage has not be initialized")
    return _store.delete(service)


def health():
    if not _store:
        raise RuntimeError("storage has not be initialized")
    return _store.health()

