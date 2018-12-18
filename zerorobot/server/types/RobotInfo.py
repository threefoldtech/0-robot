# DO NOT EDIT THIS FILE. This file will be overwritten when re-running go-raml.

"""
Auto-generated class for RobotInfo
"""
from .EnumRobotInfoType import EnumRobotInfoType
from .RobotInforepositories import RobotInforepositories

from . import client_support


class RobotInfo(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(**kwargs):
        """
        :type repositories: RobotInforepositories
        :type storage_healthy: bool
        :type type: EnumRobotInfoType
        :rtype: RobotInfo
        """

        return RobotInfo(**kwargs)

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'RobotInfo'
        data = json or kwargs

        # set attributes
        data_types = [RobotInforepositories]
        self.repositories = client_support.set_property(
            'repositories', data, data_types, False, [], False, True, class_name)
        data_types = [bool]
        self.storage_healthy = client_support.set_property(
            'storage_healthy', data, data_types, False, [], False, False, class_name)
        data_types = [EnumRobotInfoType]
        self.type = client_support.set_property('type', data, data_types, False, [], False, False, class_name)

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)

