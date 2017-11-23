
import importlib.util
import sys
import os


class TemplateNameError(Exception):
    pass


class TemplateCollection:

    def __init__(self):
        self._templates = {}

    def add_repo(self, url):
        raise NotImplementedError()

    def _load_template(self, file_path):
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

        self._templates[name] = eval('module.%s' % class_name)
