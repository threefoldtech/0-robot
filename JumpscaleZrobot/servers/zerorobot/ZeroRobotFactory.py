from Jumpscale import j

from .ZeroRobotServer import ZeroRobotServer

JSConfigBase = j.tools.configmanager.JSBaseClassConfigs


class ZeroRobotFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.zrobot"
        JSConfigBase.__init__(self, ZeroRobotServer)

