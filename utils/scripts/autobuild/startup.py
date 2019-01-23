import shlex
import os
from jose import jwt

from jumpscale import j

from zerorobot.config.data_repo import _parse_zdb

logger = j.logger.get('zrobot_statup')

iyo_pub_key = """-----BEGIN PUBLIC KEY-----
MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n2
7MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny6
6+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv
-----END PUBLIC KEY-----"""


def configure_local_client():
    j.sal.fs.createDir('/opt/code/local/stdorg/config/j.clients.zos_protocol')
    j.sal.fs.writeFile('/opt/code/local/stdorg/config/j.clients.zos_protocol/local.toml', """
    db = 0
    host = '127.0.0.1'
    password_ = ''
    port = 6379
    ssl = true
    timeout = 120
    unixsocket = '/tmp/redis.sock'
    """)


def get_admin_organization(kernel_args):
    """
    decide which organization to use to protect admin endpoint of the 0-robot API

    first we check if there is a farmer_id token
    if it exists, we extract the organization from it and use it
    if it doesn't we check if there is an organization kernel parameter and use it
    if still don't have an organization, we return None
    """

    org = None
    token = kernel_args.get('farmer_id')
    if token:
        try:
            claims = jwt.decode(token, iyo_pub_key)
        except jwt.ExpiredSignatureError:
            logger.info("farmer_id expired, trying to refresh")
            try:
                token = j.clients.itsyouonline.refresh_jwt_token(token)
            except Exception as err:
                logger.error('fail to refresh farmer_id. \
                To fix this, generate a new farmer id, update your kernel with it and reboot the machine')
                raise

            claims = jwt.decode(token, iyo_pub_key)

        for scope in claims.get('scope'):
            if scope.find('user:memberof:') != -1:
                org = scope[len('user:memberof:'):]
                break
    else:
        org = kernel_args.get('admin_organization')
        if not org:
            org = kernel_args.get('organization')

    logger.info("admin organization found: %s" % org)
    return org


def get_user_organization(kernel_args):
    org = kernel_args.get('user_organization')
    if org:
        logger.info("user organization found: %s" % org)
    return org


def read_kernel():
    """
    read the kernel parameter passed to the host machine
    return a dict container the key/value of the arguments
    """
    with open('/proc/cmdline') as f:
        line = f.read()

    args = {}
    line = line.strip()
    for kv in shlex.split(line):
        ss = kv.split('=', 1)
        if len(ss) == 2:
            args[ss[0]] = ss[1]
        elif len(ss) <= 1:
            args[ss[0]] = None
    return args


def migrate_from_zeroos_to_threefold():
    zeroos_services = '/opt/var/data/zrobot/zrobot_data/github.com/zero-os'
    if j.sal.fs.exists(zeroos_services):
        j.sal.fs.removeDirTree(zeroos_services)


def read_config_repo_config():
    """
    detect if zdb data repository is configured and return the url to the zdb if any

    :return: zdb url or None if not configured
    :rtype: str or None
    """

    logger.info("detect if zdb data repository is configured")

    data_path = '/opt/var/data/zrobot/zrobot_data/data_repo.yaml'
    if not j.sal.fs.exists(data_path):
        logger.info("no zdb data repository configuration found")
        return None

    repo = j.data.serializer.yaml.load(data_path)
    zdb_url = repo.get('zdb_url')
    if not zdb_url:
        logger.error("wrong format in zdb data repository configuration")
        return None

    try:
        _parse_zdb(zdb_url)
        return zdb_url
    except ValueError:
        logger.error("zdb url has wrong format in zdb data repository configuration: %s", zdb_url)
        return None


def start_robot():
    kernel_args = read_kernel()
    args = ['zrobot', 'server', 'start', '--mode', 'node']

    admin_org = get_admin_organization(kernel_args)
    if admin_org:
        args.extend(['--admin-organization', admin_org])

    user_org = get_user_organization(kernel_args)
    if user_org:
        args.extend(['--user-organization', user_org])

    if 'development' in kernel_args or 'god' in kernel_args or 'support' in kernel_args:
        args.append('--god')

    zdb_url = read_config_repo_config()
    if zdb_url:
        args.extend(['--data-repo', zdb_url])

    template_repo = 'https://github.com/threefoldtech/0-templates#master'
    args.extend(['--template-repo', template_repo])

    logger.info('starting node robot: %s', ' '.join(args))

    os.execv('usr/local/bin/zrobot', args)


def main():
    migrate_from_zeroos_to_threefold()
    configure_local_client()
    start_robot()


if __name__ == '__main__':
    main()
