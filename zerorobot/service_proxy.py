from .template import TemplateBase


class ServiceProxy(TemplateBase):
    """
    This class is used to provide a local proxy to a remote service for a ZeroRobot.
    When a service or robot ask the creation of a service to another robot, a proxy class is created locally
    so the robot see the service as if it as local to him while in reality the service is managed by another robot.
    """

    def __init__(self, name, guid=None):
        super().__init__(name, guid)
        # a proxy service doesn't have direct access to the data of it's remote omologue
        # cause data are always only accessible  by the service itself and locally
        self.data = None
