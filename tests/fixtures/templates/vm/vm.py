from zerorobot.template.base import TemplateBase


class Vm(TemplateBase):

    version = '0.0.1'
    template_name = "vm"

    def __init__(self, name, guid=None):
        super().__init__(name=name, guid=guid)

    def start(self):
        print('started')

    def stop(self):
        print('stop')
