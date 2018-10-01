"""
this module contain class that are used to store the data repository configration of the robot
"""

import os
from urllib.parse import urlparse

from jumpscale import j
from zerorobot.git import url as giturl

from .auto_pusher import AutoPusher


class DataRepo:

    def __init__(self, url):
        self.url = None
        self.path = None
        self.auto_pusher = None
        self.username = None
        self.password = None
        self.hostname = None
        self.port = None
        self.namespace = None
        self.type = None

        path = j.sal.fs.joinPaths(j.core.dirs.DATADIR, 'zrobot')

        # test if url points to a zdb
        if url:
            try:
                self.password, self.hostname, self.port, self.namespace = _parse_zdb(url)
                self.type = 'zdb'
                # needed cause some code expect to have a path always set,
                # even if we're not going to actually save data there
                self.path = path
                return
            except ValueError:
                # not a zdb url, try git url
                pass

            try:
                # try to see of path is a git URL
                path = giturl.git_path(url)
                self.url = url
                # if the repo is not clone yet, clone it now
                if not os.path.exists(path):
                    path = j.clients.git.pullGitRepo(url)
            except ValueError:
                # not a zdb url, try absolute path
                path = url

        # path is not an URL, we expect an absolute path
        if not os.path.isabs(path):
            raise ValueError("path value is not valid. Need to be a valid git url or an absolute path on the local filesystem")

        path = os.path.join(path, 'zrobot_data')

        if not os.path.exists(path):
            os.makedirs(path)

        self.path = path
        self.type = 'fs'

    @property
    def last_pushed(self):
        if not self.auto_pusher:
            return None
        return self.auto_pusher.last_pushed

    def start_auto_push(self, interval=60, logger=None):
        self.auto_pusher = AutoPusher(interval, self.path, logger)
        self.auto_pusher.run()


def _parse_zdb(line):
    """
    parse a zdb url

    zdb://admin_password@hostname:port/namespace

    return (admin_password, hostname, port, namespace)
    """

    u = urlparse(line)
    if u.scheme != 'zdb':
        raise ValueError('scheme should be bcdb, not %s', u.scheme)

    path = u.path[1:] if u.path and u.path[0] == '/' else u.path

    return (u.username, u.hostname, u.port, path)
