"""
this module is the only place where the templates will be kept in memory.
other services and class need to use this module method to load/access the templates
"""

import importlib.util
import sys
import os
from urllib.parse import urlparse

from zerorobot import service_collection as scol

from js9 import j

_templates = {}


def add_repo(url, branch='master', directory='templates'):
    """
    url: url of a git repository e.g: http://github.com/jumpscale/zeroroot
    branch: the branch of the repository to checkout
    directory: the path to the directory where the templates are located in the repository
    """
    new_templates = []
    dir_path = j.clients.git.getContentPathFromURLorPath(url)
    if not os.path.exists(dir_path):
        dir_path = j.clients.git.pullGitRepo(url)
    for path in j.sal.fs.listDirsInDir(j.sal.fs.joinPaths(dir_path, directory)):
        if j.sal.fs.getBaseName(path) == '__pycache__':
            continue
        new_templates.append(_load_template(url, path))
    return new_templates


def get(uid):
    """
    @uid: unique identifier for a template.
    Can be a string with valid format as : 'github.com/account/repository/name/version'
    or
    a zerorobot.template_collection.TemplateUID object
    """
    if isinstance(uid, str):
        uid = TemplateUID.parse(uid)
    if uid not in _templates:
        raise KeyError("template with name %s not found" % str(uid))
    return _templates[uid]


def list_templates():
    return list(_templates.values())


def _load_template(url, template_dir):
    """
    load a template in memory from a file
    The file must contain a class that inherits from template.TemplateBase
    and the name of the class must match the name of the file.
    the name of the class is camelcased from the name of the file.
    ex:
        node.py -> Node
        vm_manager.py -> VmManager
        a_long_name.py -> ALongName
    """
    template_name = os.path.basename(template_dir).split('.')[0]
    class_name = template_name.replace('_', ' ').title().replace(' ', '')
    class_path = j.sal.fs.joinPaths(template_dir, template_name + '.py')

    spec = importlib.util.spec_from_file_location(template_name, class_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if class_name not in module.__dict__:
        raise TemplateNameError("template %s should contain a class called %s" % (template_name, class_name))

    class_ = eval('module.%s' % class_name)

    _, host, account, repo, _, _ = j.clients.git.rewriteGitRepoUrl(url)

    class_.template_uid = TemplateUID.parse("%s/%s/%s/%s/%s" % (host, account, repo, template_name, class_.version))

    class_.template_dir = template_dir
    _templates[class_.template_uid] = class_
    return _templates[class_.template_uid]


def instanciate_service(template, name, data=None):
    if isinstance(template, str):
        template = get(template)

    service = template(name)
    if data is not None:
        service.data.update(data)

    scol.add(service)
    return service


class TemplateUID:

    def __init__(self, host, account, repo, name, version):
        self.host = host
        self.account = account
        self.repo = repo
        self.name = name
        self.version = version

    @classmethod
    def parse(cls, uid):
        """
        Parse a template unique identifier.
        A tempate is identify by the url fo the git repository from where it comes from.
        There are different information extracted from
        - the host
        - the account
        - the repository name
        - the name of the template itself
        - a version
        e.g: https://github.com/account/repository/name/version would result into
        host: github.com
        account: account
        repository name: repository
        template name: name
        version: version
        """
        host, account, repo, name, version = None, None, None, None, None

        parsed = urlparse(uid)
        if parsed.netloc:
            host = parsed.netloc

        path = parsed.path.rstrip('/').lstrip('/')

        ss = path.split('/')

        if host is None and len(ss) == 5:
            host, account, repo, name, version = ss
        elif host is not None and len(ss) == 4:
            account, repo, name, version = ss
        else:
            raise ValueError("format of the template uid (%s) not valid" % uid)

        return cls(host, account, repo, name, version)

    def tuple(self):
        return (self.host, self.account, self.repo, self.name, self.version)

    def __repr__(self):
        return '/'.join(self.tuple())

    def __str__(self):
        return repr(self)

    def __comp(self, other):
        if self.tuple()[:-1] != other.tuple()[:-1]:
            raise ValueError("other is not the same template, can't compare version")
        if self.version < other.version:
            return -1
        elif self.version > other.version:
            return 1
        else:
            return 0

    def __eq__(self, other):
        if not isinstance(other, TemplateUID):
            raise ValueError("other is not an instance of TemplateUID")

        return self.tuple() == other.tuple()

    def __lt__(self, other):
        return self.__comp(other) == -1

    def __le__(self, other):
        return self.__comp(other) in [0, -1]

    def __gt__(self, other):
        return self.__comp(other) == 1

    def __ge__(self, other):
        return self.__comp(other) in [0, 1]

    def __hash__(self):
        return hash(self.tuple())


class TemplateNameError(Exception):
    pass
