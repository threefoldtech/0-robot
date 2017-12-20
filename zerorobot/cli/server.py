
from gevent import monkey

# need to patch sockets to make requests async
monkey.patch_all()

import click
from js9 import j

from zerorobot.robot import Robot


@click.group()
def server():
    pass


@server.command()
@click.option('--listen', '-L', help='listen address (default :6600)', default=':6600')
@click.option('--data-repo', '-D', required=True, help='URL of the git repository where to save the data of the zero robot')
@click.option('--template-repo', '-T', multiple=True, help='list of template repository URL')
@click.option('--robots', '-R', multiple=True, help='address of reachable robots')
@click.option('--debug', help='enable debug logging', is_flag=True, default=False)
def start(listen, data_repo, template_repo, robots, debug):
    """
    start the 0-robot daemon.
    this will start the REST API on address and port specified by --listen and block
    """
    if debug:
        j.logger.set_level("DEBUG")

    robot = Robot()

    for url in template_repo:
        robot.add_template_repo(url)

    for addr in robots:
        robot.add_remote_robot(addr)

    robot.set_data_repo(data_repo)
    robot.start(listen=listen)
