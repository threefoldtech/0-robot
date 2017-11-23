"""
this module is the only place where the templates will be kept in memory.
other services and class need to use this module method to load/access the templates
"""

import importlib.util
import sys
import os

from js9 import j

_templates = {}


def add_repo(url):
    dir_path = j.clients.git.getContentPathFromURLorPath(url)
    for path in j.sal.fs.listFilesInDir(j.sal.fs.joinPaths(dir_path, 'templates')):
        _load_template(path)


def get_template(name):
    if name not in _templates:
        raise KeyError("template with name %s not found" % name)
    return _templates[name]


def _load_template(file_path):
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
    name = os.path.basename(file_path).split(os.path.extsep)[0]
    class_name = name.replace('_', ' ').title().replace(' ', '')

    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if class_name not in module.__dict__:
        raise TemplateNameError("template %s should contain a class called %s" % (name, class_name))

    _templates[name] = eval('module.%s' % class_name)


class TemplateNameError(Exception):
    pass
