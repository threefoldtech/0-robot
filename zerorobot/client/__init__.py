"""
This package is generated using [go-raml](https://github.com/Jumpscale/go-raml)

It is the client of the REST API of the ZeroRobot
"""


import requests


from .Action import Action
from .Blueprint import Blueprint
from .EnumServiceStateState import EnumServiceStateState
from .EnumTaskState import EnumTaskState
from .Error import Error
from .Service import Service
from .ServiceCreate import ServiceCreate
from .ServiceState import ServiceState
from .Task import Task
from .TaskCreate import TaskCreate
from .Template import Template
from .TemplateRepository import TemplateRepository

from .client import Client as APIClient


class Client:

    def __init__(self, base_uri=""):
        self.api = APIClient(base_uri)
