#!/usr/bin/env python3

from gevent import monkey
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


from zerorobot.robot import Robot


def main():
    robot = Robot()
    robot.start()

if __name__ == "__main__":
    main()
