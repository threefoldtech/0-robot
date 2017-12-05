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

import click

from zerorobot.robot import Robot


@click.command()
@click.option('--data-repo', '-D', required=True, help='URL of the git repository where to save the data of the zero robot')
@click.option('--template-repo', '-T', multiple=True, help='list of templare repository URL')
def main(data_repo, template_repo):
    robot = Robot()
    for url in template_repo:
        robot.add_template_repo(url)
    robot.set_data_repo(data_repo)
    robot.start()

if __name__ == "__main__":
    main()
