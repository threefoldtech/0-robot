"""
this module is the only place where the templates will be kept in memory.
other services and class need to use this module method to load/access the templates
"""

import importlib.util
import sys
import os

from js9 import j

_templates = {}


def add_repo(url, branch='master'):
    new_templates = []
    dir_path = j.clients.git.pullGitRepo(url)
    for path in j.sal.fs.listDirsInDir(j.sal.fs.joinPaths(dir_path, 'templates')):
        if j.sal.fs.getBaseName(path) == '__pycache__':
            continue
        new_templates.append(_load_template(path))
    return new_templates


def get(name):
    if name not in _templates:
        raise KeyError("template with name %s not found" % name)
    return _templates[name]


def list_templates():
    return list(_templates.values())


def _load_template(template_dir):
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

    _templates[template_name] = eval('module.%s' % class_name)
    return _templates[template_name]


class TemplateNameError(Exception):
    pass
