from zerorobot.template import TemplateBase


class Node(TemplateBase):

    version = '0.0.1'
    template_name = "node"

    def __init__(self, name, guid=None):
        super().__init__(name=name, guid=guid)

    def start(self):
        print('started')

    def stop(self):
        print('stop')

    def foo(self, bar):
        print('foo')
