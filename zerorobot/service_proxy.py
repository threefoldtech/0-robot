
from zerorobot.template import ServiceState


class ServiceProxy():
    """
    This class is used to provide a local proxy to a remote service for a ZeroRobot.
    When a service or robot ask the creation of a service to another robot, a proxy class is created locally
    so the robot see the service as if it as local to him while in reality the service is managed by another robot.
    """

    def __init__(self, name, guid, zrobot_client):
        self._zrobot_client = zrobot_client
        self.name = name
        self.guid = guid
        # a proxy service doesn't have direct access to the data of it's remote omologue
        # cause data are always only accessible  by the service itself and locally
        self.data = None
        self.state = ServiceState()

    def schedule_action(self, action, args=None, resp_q=None):
        """
        Do a call on a remote ZeroRobot to add an action to the task list of
        the corresponding service

        @param action: action is the name of the action to add to the task list
        @param args: dictionnary of the argument to pass to the action
        @param resp_q: is the response queue on which the result of the action need to be put
        """
        req = {
            "action_name": action,
        }
        if args:
            req["args"] = args
        resp = self._zrobot_client.api.services.AddTaskToList(req, service_guid=self.guid)
        return resp.data

    def delete(self):
        self._zrobot_client.api.services.DeleteService(self.guid)
