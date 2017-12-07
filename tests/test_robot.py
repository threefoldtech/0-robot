import unittest

from zerorobot.robot import Robot


class TestRobot(unittest.TestCase):

    def test_add_data_repo(self):
        robot = Robot()
        url = 'https://github.com/jumpscale/zerorobot'
        robot.set_data_repo(url)
        self.assertEqual(robot._data_dir, '/opt/code/github/jumpscale/zerorobot/zrobot_data')
        self.assertEqual(robot.data_repo_url, url)

    def test_data_dir_required(self):
        robot = Robot()
        with self.assertRaises(RuntimeError, msg="robot should not start if not data dir set"):
            robot.start()
