
# Introduction and concepts

### Template
A template is like its name suggests; a template for a service. In practice this is just a python class that implements some methods and have some properties.

A 0-Robot's main task is to clone some git repositories where these templates are located and load them into memory. They are then ready to be instantiated into services.

### Service
A service is an instance of a template.  
Once a service is created, it can start to actually execute some actions.
The actions to be executed are asked by the user or by another service.

Each service has its own task list. This is a queue where all the required actions are stacked and processed one by one.

Some services will depend on other services to be able to complete an action. Let's call the dependent service a _producer_.  
When a service is asked to execute an action and requires some producer to do something for it, it will add this action to the task list of the producer.

The producer will then eventually pick the task and execute the required action. The execution of the producer's action can create a result that can be sent back to the service that ask for it.

By combining different services and actions we can create a distributed system that can scale. Also, the fact that a service is only responsible for a really specific task allows us to keep the code clean and concise. 

### Technically
From a technological perspective, a 0-Robot is a gevent greenlet that is responsible to handling requests from users. Requests are for example, create this service or give me the state of these services.

Each service is also running in a greenlet and is watching a queue; _the task list_. The service is responsible for consuming all the task from its queue to execute the action required by the user or other services. The communication between services always happens through queue. This is to ensure serialization of the action and non-concurrent access to the data.

So when a service adda a task to a producer's task list, it also provide a response queue on which the producer need to write to send the result of the action back to the originating service.

Each 0-Robot also exposes a REST API, to allow communication between different 0-Robots. So when a service asks for an action from a service that is managed by another robot, the request is transported though a REST call to the remote robot. All of this happens on behalf of the user and it doesn't really have to know where the service is located, only that what it can provide in term of actions.

