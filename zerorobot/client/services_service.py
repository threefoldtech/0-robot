
from .Action import Action
from .Service import Service
from .Task import Task
from .api_response import APIResponse
from .unmarshall_error import UnmarshallError

class ServicesService:
    def __init__(self, client):
        self.client = client



    def ListActions(self, service_guid, headers=None, query_params=None, content_type="application/json"):
        """
        List all the possible action a service can do.
        It is method for GET /services/{service_guid}/actions
        """
        uri = self.client.base_url + "/services/"+service_guid+"/actions"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            resps = []
            for elem in resp.json():
                resps.append(Action(elem))
            return APIResponse(data=resps, response=resp)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except Exception as e:
            raise UnmarshallError(resp, e.message)
        


    def GetTask(self, task_guid, service_guid, headers=None, query_params=None, content_type="application/json"):
        """
        Retrieve the detail of a task
        It is method for GET /services/{service_guid}/task_list/{task_guid}
        """
        uri = self.client.base_url + "/services/"+service_guid+"/task_list/"+task_guid
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            return APIResponse(data=Task(resp.json()), response=resp)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except Exception as e:
            raise UnmarshallError(resp, e.message)
        


    def getTaskList(self, data, service_guid, headers=None, query_params=None, content_type="application/json"):
        """
        Return all the action in the task list
        It is method for GET /services/{service_guid}/task_list
        """
        uri = self.client.base_url + "/services/"+service_guid+"/task_list"
        return self.client.get(uri, data, headers, query_params, content_type)


    def AddTaskToList(self, data, service_guid, headers=None, query_params=None, content_type="application/json"):
        """
        Add a task to the task list
        It is method for POST /services/{service_guid}/task_list
        """
        uri = self.client.base_url + "/services/"+service_guid+"/task_list"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            return APIResponse(data=Task(resp.json()), response=resp)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except Exception as e:
            raise UnmarshallError(resp, e.message)
        


    def DeleteService(self, service_guid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete a service
        It is method for DELETE /services/{service_guid}
        """
        uri = self.client.base_url + "/services/"+service_guid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetService(self, service_guid, headers=None, query_params=None, content_type="application/json"):
        """
        Get the detail of a service
        It is method for GET /services/{service_guid}
        """
        uri = self.client.base_url + "/services/"+service_guid
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            return APIResponse(data=Service(resp.json()), response=resp)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except Exception as e:
            raise UnmarshallError(resp, e.message)
        


    def listServices(self, headers=None, query_params=None, content_type="application/json"):
        """
        List all the services known by the ZeroRobot.
        It is method for GET /services
        """
        uri = self.client.base_url + "/services"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            resps = []
            for elem in resp.json():
                resps.append(Service(elem))
            return APIResponse(data=resps, response=resp)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except Exception as e:
            raise UnmarshallError(resp, e.message)
        


    def createService(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        create a new service
        It is method for POST /services
        """
        uri = self.client.base_url + "/services"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            return APIResponse(data=Service(resp.json()), response=resp)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except Exception as e:
            raise UnmarshallError(resp, e.message)
        
