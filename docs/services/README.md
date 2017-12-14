# Services

- [Service data](#service_data)
- [Service state](#service_state)
- [Service Actions](#service_action)

## Service data
The services data is the information that a service needs to receive to be created and the information the services gather during its lifetime. The data of a service is always private and is never going to be shared with another service or client. The service itself is the only one to have access to its data.

The definition of which data needs to be given is specified in the template schema. This schema is a capnp object, in which we define the data of the services.

Example of a schema:
```capnp
@0xc5ba0f64c9013a79;

struct Schema {
    id @0: Text; # mac address of the mngt network card
    hostname @1: Text;

    redisAddr @2 :Text; # redis addr for client
    redisPort @3 :UInt32 = 6379; # redis port for client
    redisPassword @4 :Text; # redis password for client
    version @5 :Text;
}
```

From within a service, you can access it with the `data` attribute of the service class. This attribute is a dictionary that maps to the definition of the schema. Trying to access key that are not defined in the schema, will raise an exception.

example:
```python
class Node(TemplateBase):

    version = '0.0.1'
    template_name = "node"

    def __init__(self, name, guid=None):
        super().__init__(name=name, guid=guid)

    def foo(self):
        # access the data of the service
        print(self.data['hostname'])
        # update the data of the service
        self.data['version'] = "1.1.1"
        # this line will raise
        self.data['randomkey'] = 'value'
```

## Service state
The service state holds the information regarding the health of a service as well as some basic states.

The service state is organized per category, in each category, there can be tags and associated with a tag, a state.

So an example of a service state could be:
```
- actions
  - installed: ok
  - started: ok
- network
  - tcp-80: ok
  - tcp-8080: error
```

Category and tags can be any string. There is not restriction. But the state associated needs to be one of `'new'`, `'ok'` or `'error'`


The service state management is completely left to the developer of the service. It is up to him to change the state a when needed.

The developer can also check the state of a another service to take decision.

See the detail API documentation about the service state for more detail about the interface: https://jumpscale.github.io/zerorobot/api/zerorobot/template/base.m.html#zerorobot.template.base.ServiceState

Example:
```python
class Node(TemplateBase):

    version = '0.0.1'
    template_name = "node"

    def __init__(self, name, guid=None):
        super().__init__(name=name, guid=guid)

    def foo(self):
        try:
            # check if the status of foo:bar is error
            self.state.check('foo','bar', 'error')
            # ....
        except StateCheckError:
            # if state is not error, StateCheckError is raised
            # .... do the work
        
        # set the state
        self.state.set('foo', 'bar', 'ok)
        # read the state
        state = self.state.get('foo','bar')
        # state variable will contain {'bar': 'ok'}

```
## Service actions

The services actions is the core of a service logic.
An actions is just a method on the service object.

### Customize actions behavior
It is possible to add some special behavior to an actions using decorators
See the API documentation for more detail: https://jumpscale.github.io/zerorobot/api/zerorobot/template/decorator.m.html

#### Rety decorator
This decorator allows to define retry policy for the action. 
In case the action raises an exception during it's execution, the action is going to be retied according to the policy defined with the decorator arguments.

Arguments of the decorator:
- exceptions: The exception to check. may be a tuple of exceptions to check.
- tries: Number of times to try (not retry) before giving up. 
- delay: Initial delay between retries in seconds. 
- backoff: Backoff multiplier (e.g. value of 2 will double the delay each retry). 
- logger: Logger to use. If None, print.


#### Timeout decorator
This decorator allow to set a maximum execution time for an action. It will raise a `TimeoutError` if the wrapped action takes more time then the timeout value to execute.

Arguments of the decorator:
- seconds: timeout time in seconds 
- error_message: message to pass to the TimeoutError exception raised