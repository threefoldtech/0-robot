import logging
import os
import signal
import tempfile

import gevent
from gevent.pywsgi import WSGIServer
from gevent.pool import Pool

from js9 import j

from zerorobot.api.app import app
from zerorobot import service_collection as scol
from zerorobot import template_collection as tcol


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
        self._sig_handler = []

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

    def add_template_repo(self, url):
        tcol.add_repo(url)

    def start(self, host='0.0.0.0', port=6600, log_level=logging.DEBUG):
        """
        start the rest web server
        load the services from the local git repository
        """
        if self._data_dir is None:
            raise RuntimeError("Not data repository set. Robot doesn't know where to save data.")

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
        self._http = WSGIServer((host, port), app, spawn=pool, log=app.logger, error_log=app.logger)

        app.logger.info("robot running at %s:%s" % (host, port))

        self._http.serve_forever()

    def stop(self):
        """
        stop receiving requests
        gracefully stop all the services
        serialize all services state to disk
        """
        # prevent the signal handler to be called again is
        # more signal are received
        for h in self._sig_handler:
            h.cancel()

        print('stopping robot')
        self._http.stop()

        # here no more requests are comming in
        # all services should have received kill signal
        self._save_services()

    def _load_services(self):
        for srv_dir in j.sal.fs.listDirsInDir(self._data_dir):
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
