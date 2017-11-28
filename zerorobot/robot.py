import gevent
from gevent.pywsgi import WSGIServer
from gevent.pool import Pool
import signal

from js9 import j

from zerorobot.api.app import app


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
        self.data_repo_url = url
        location = j.clients.git.pullGitRepo(url=url)
        self._data_dir = j.sal.fs.joinPaths(location, 'zero_robot_data')

    def start(self, host='0.0.0.0', port=6600):
        """
        start the rest web server
        load the services from the local git repository
        """
        self._sig_handler.append(gevent.signal(signal.SIGQUIT, self.stop))
        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))

        # using a pool allow to kill the request when stopping the server
        pool = Pool(None)
        self._http = WSGIServer((host, port), app, spawn=pool)
        print("robot running at %s:%s" % (host, port))
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
