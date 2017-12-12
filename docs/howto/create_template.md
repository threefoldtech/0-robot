# How to create a new template

## Minimal code:
```python
from zerorobot.template.base import TemplateBase


class MyTemplate(TemplateBase):

    version = '0.0.1'
    template_name = "mytemplate"

    def __init__(self, name, guid=None):
        super().__init__(name=name, guid=guid)
```