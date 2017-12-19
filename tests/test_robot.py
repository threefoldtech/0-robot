import tempfile
import unittest

from gevent import monkey
from zerorobot.robot import Robot

# need to patch sockets to make requests async
monkey.patch_all(
    socket=True,
    dns=True,
    time=True,
    select=True,
    thread=True,
    os=True,
    ssl=True,
    httplib=False,
    subprocess=False,
    sys=False,
    aggressive=True,
    Event=False,
    builtins=True,
    signal=True)


class TestRobot(unittest.TestCase):

    def test_add_data_repo(self):
        robot = Robot()
        url = 'https://github.com/jumpscale/0-robot'
        robot.set_data_repo(url)
        self.assertEqual(robot._data_dir, '/opt/code/github/jumpscale/0-robot/zrobot_data')
        self.assertEqual(robot.data_repo_url, url)

    def test_data_dir_required(self):
        robot = Robot()
        with self.assertRaises(RuntimeError, msg="robot should not start if not data dir set"):
            robot.start()

    def test_address(self):
        robot = Robot()
        self.assertIsNone(robot.address)
        with tempfile.TemporaryDirectory() as data_dir:
            robot._data_dir = data_dir
            robot.start(listen="localhost:6600", block=False)
            self.assertEqual(robot.address, ('127.0.0.1', 6600))
            robot.stop()
        self.assertIsNone(robot.address)
