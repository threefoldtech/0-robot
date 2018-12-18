from zerorobot.template.base import TemplateBase


class Recurring(TemplateBase):

    version = '0.0.1'
    template_name = "recurring"

    def __init__(self, name, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self.recurring_action('monitor', 10)

    def monitor(self):
        print('monitor')

