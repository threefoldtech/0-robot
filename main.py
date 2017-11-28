#!/usr/bin/env python3

# from gevent import monkey
# # need to patch sockets to make requests async
# monkey.patch_all()


from zerorobot.robot import Robot


def main():
    robot = Robot()
    robot.start()

if __name__ == "__main__":
    main()
