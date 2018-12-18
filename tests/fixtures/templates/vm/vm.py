from zerorobot.template.base import TemplateBase


class Vm(TemplateBase):

    version = '0.0.1'
    template_name = "vm"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)

    def start(self):
        print('started')

    def stop(self):
        print('stop')

