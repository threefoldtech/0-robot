# Glossary

## Index
- [action](#action)
- [Blueprint](#blueprint)
- [DNS name](#dns-name)
- [DSL](#dsl)
- [Model](#model)
- [Proxy](#proxy)
- [Robot](#robot)
- [Service](#service)
- [State](#state)
- [Task](#task)
- [Task list](#task-list) 
- [Template](#template)

### Action
An action is the description of what needs to happens for a service to execute a task. The code of the action is written using the [DSL](#dsl).
If a service needs some action from another service to finish is own action, the service needs to ask to add the required action on the task list of the other service. 
### Blueprint
A blueprint is a description of which [service](#service) needs to be created and which [action](#action) needs to executed. 
It's written in yaml.

### data
Service data model: This is model that represent the specific data bind to a service. The schema used to define this model is capnp. The data of a service is only accessible by the service itself, it will never be exposed to a remote service. If some information need to be shared, it need to be communicated through an action.

### DSL
DLS stands for "domain specific language". This is the language used in the [template](#template) [action](#action) to describe what needs to be done to execute an [action](#action).

The DLS we use is actually some python code. Some easy to use module have been created inside [Jumpscale](https://github.com/Jumpscale/home) and are supposed to be re-used inside the [template](#template) [action](#action)


### Proxy
A service proxy is a local representation of the state of a remote service. This allow the robot to always work the same way would it be talking to a local service or a remote one. The complexity of the network communication is hidden by the proxy service.

### Robot
A robot is the main context in which all the [templates](#template) and [services](#service) lives.  
It's expose a REST api that is used to receives request from other robots or users.
It's also the one responsible to download template from git repository and make template available to be used inside himself.

### Service
A service in an instance of a [template](#template). Each service is instantiated from a specific version of a template.
A service can be created by the request of a user though a blueprint, or from an [action](#action) of another service.

### State
Every service have a list of state. It gives information about the service. Each state has a category & tag & state
format: $category:$tag:$state
state is ok or error

e.g.: 

- data:db:ok
- network:local-tcp-443:ok
- network:remote-http-80: ok
- process:mongod:ok


### Task
A task is what result after an action has been asked to be executed. When a user ask a [service](#service) to execute an [action](#action) from a [blueprint](#blueprint), a multitude of task are added to the task list of one or multiple [ZeroRobot](#robot)

### Task list
A task list is all [tasks](#task) that a [ZeroRobot](#robot) still need to execute.
By following the task list of a [ZeroRobot](#robot) we can generate in real time a dependency graph of what is still going to be executed for a specific [action](#action).

### Template
A template is the source of a service. It contains the definition of the [actions](#action) of a service.  
A [service](#service) is always instantiated from a specific version of a template

