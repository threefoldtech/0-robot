

## only 2 root objects

- templates
- services

## zrobot

- is a gevent service which has an own private/public key
- a zrobot fetches templates from X repo's
- a zrobot runs Y services
- a zrobot stores the services state into a git repo
- a zrobot will sign the changes into the git repo

## templates

- have strict versioning and services depend on specific template

## service

### service_state

each service_state has a category & tag & state
a service has multiple states

format: $category:$tag:$state
state is ok or error

e.g.: 

- data:db:ok
- network:local-tcp-443:ok
- network:remote-http-80: ok
- process:mongod:ok

## 2 types of actions

### service_action

- init
- start
- stop
- monitor
- import
- export
- delete

each action has following states

- new (means waiting)
- ok
- error

there are NO automatic service action dependencies
each action needs to implement what they require e.g.

export -> stop (if start=ok and datastate=ok), 
start -> init (if init=new)
monitor -> start
import -> init
... 

### reality_action

executes something in the field, can have any name and get's predefined arguments & output


## action queue

is queue of actions to be done for own service as well as related services (eg parent or producer of service to us)

e.g.

- self->init
- hypervisor.kvm.1->start
- hypervisor.kvm.1->start

## vrobot

- executes actions from templates (in process or not)


