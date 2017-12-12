# Template

A template is the source of a service.  
It contains the definition of the [actions](../../glossary.md#action), the configuration and the data schema of a [service](../../glossary.md#service).

## Template Unique Identifier (template UID)
A tempate is identify by the url fo the git repository from where it comes from.  
There are different information extracted from the URL:
- the host
- the account
- the repository name
- the name of the template itself
- a version

e.g: github.com/jumpscale/zerorobot/node/1.0.0 would result into
```
host: github.com
account: jumpscale
repository name: zerorobot
template name: node
version: 1.0.0
```

When creating a new service, the user needs to refer to the template use with its template UID.

This snippet of code show how to create a new service using a template UID:
```python
from zerorobot import template_collection as tcol

template_uid = "github.com/jumpscale/zerorobot/node/1.0.0"
name = "container1"
args = {'foo': 'bar'}
container = tcol.instanciate_service(template_uid, name, args)
```