"""
robot modules define the Robot class

It is the class responsible to start and managed the robot as well as the REST API.
"""

import logging
import os
import signal
import tempfile

import gevent
from gevent import GreenletExit
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer
from js9 import j
from JumpScale9.core.State import ClientConfig
from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol
from zerorobot.api.app import app
from zerorobot.task import PRIORITY_SYSTEM, Task


class Robot:
    """
    A robot is the main context where the templates and service lives.
    It is responsible to:
        - run the REST API server
        - download the template from a git repository
        - load the templates in memory and make them available
    """

    def __init__(self):
        self._started = False
        self.data_repo_url = None
        self._data_dir = None
        self._http = None  # server handler
        self.addr = None
        self._sig_handler = []
        self._autosave_gl = None

    @property
    def address(self):
        if self._http:
            return self._http.address
        return None

    def set_data_repo(self, url):
        """
        Set the url of the git repository to be used to serialize services state.
        It can be the same of one of the template repository used.
        """
        location = j.clients.git.getContentPathFromURLorPath(url)
        if not os.path.exists(location):
            location = j.clients.git.pullGitRepo(url)

        self.data_repo_url = url
        self._data_dir = j.sal.fs.joinPaths(location, 'zrobot_data')

    def add_template_repo(self, url, branch='master', directory='templates'):
        tcol.add_repo(url=url, branch=branch, directory=directory)

    def add_remote_robot(self, addr):
        """
        configure a remote robot that should be know by this robot.abs
        :param addr: HTTP URL of the other Robot API
        :type addr: string
        """
        cl = j.clients.zrobot.get(addr)
        j.clients.zrobot.set(addr, cl)

    def start(self, listen=":6600", log_level=logging.DEBUG, block=True):
        """
        start the rest web server
        load the services from the local git repository
        """
        if self._data_dir is None:
            raise RuntimeError("Not data repository set. Robot doesn't know where to save data.")

        self._autosave_gl = gevent.spawn(_auto_save_services, data_dir=self._data_dir)

        # load services from data repo
        self._load_services()

        self._sig_handler.append(gevent.signal(signal.SIGQUIT, self.stop))
        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))

        # configure logger
        app.logger.setLevel(log_level)
        app.logger.addHandler(j.logger.handlers.consoleHandler)
        app.logger.addHandler(j.logger.handlers.fileRotateHandler)

        # using a pool allow to kill the request when stopping the server
        pool = Pool(None)
        hostport = _split_hostport(listen)
        self._http = WSGIServer(hostport, app, spawn=pool, log=app.logger, error_log=app.logger)

        app.logger.info("robot running at %s:%s" % hostport)

        if block:
            self._http.serve_forever()
        else:
            self._http.start()

    def stop(self):
        """
        stop receiving requests
        gracefully stop all the services
        serialize all services state to disk
        """
        # prevent the signal handler to be called again if
        # more signal are received
        for h in self._sig_handler:
            h.cancel()

        print('stopping robot')
        self._http.stop()
        self._http = None

        if self._autosave_gl:
            self._autosave_gl.kill()

        # here no more requests are comming in
        # all services should have received kill signal
        self._save_services()

    def _load_services(self):
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir)

        for srv_dir in j.sal.fs.listDirsInDir(self._data_dir, recursive=True):
            service_info = j.data.serializer.yaml.load(os.path.join(srv_dir, 'service.yaml'))
            # TODO: template should be url+name
            tmplClass = tcol.get(service_info['template'])
            srv = tmplClass.load(srv_dir)
            scol.add(srv)

    def _save_services(self):
        """
        serialize all the services on disk
        """
        for service in scol.list_services():
            service.save(self._data_dir)


def _auto_save_services(data_dir):
    """
    this method runs in a greenlet during the lifetime of the robot
    it ask the services to saves themself every minutes

    The save method is added as a task with high priority on the services, so we don't create race conditions
    with other tasks
    """
    while True:
        try:
            for service in scol.list_services():
                service._schedule_action('save', {'base_path': data_dir}, None, PRIORITY_SYSTEM)
            gevent.sleep(60)
        except GreenletExit:
            # TODO: gracefull shutdown
            print("exit auto save greenlet")
            break


def _split_hostport(hostport):
    """
    convert a listen addres of the form
    host:port into a tuple (host, port)
    host is a string, port is an int
    """
    i = hostport.index(':')
    host = hostport[:i]
    port = hostport[i + 1:]
    return host, int(port)
