
from gevent import monkey

# need to patch sockets to make requests async
monkey.patch_all(subprocess=False)

from jumpscale import j
import click
import logging
from Jumpscale.logging.Handlers import TelegramHandler
from Jumpscale.logging.Handlers import TelegramFormatter
from zerorobot.robot import Robot


telegram_logger = logging.getLogger('telegram_logger')
telegram_logger.disabled = True


@click.group()
def server():
    pass


def get_db_config_repo():
    """Gets config repo sandbox based on the configured namespace in jumpscale.toml
    
    Returns:
        str or None: config_repo  
    """
    # configmanager will have file by default and on fresh jumpscale will have it in jumpscale.toml
    backend =  j.core.state.configGetFromDict("myconfig", "backend", "file")
    namespace_in_cfg = j.core.state.configGetFromDict("myconfig", "namespace", "default")
    config_repo = None

    if backend == "db" :
        if namespace_in_cfg:
            config_repo_path = j.sal.fs.joinPaths(j.dirs.HOMEDIR, "configmgrsandboxes", namespace_in_cfg) 
            if j.sal.fs.exists(config_repo_path):
                config_repo = config_repo_path
    return config_repo


def get_db_config_key():
    """Gets config key from sandbox based on the configured namespace in jumpscale.toml
    
    Returns:
        str or None: config_key  
    """
    backend =  j.core.state.configGetFromDict("myconfig", "backend", "file")
    namespace_in_cfg = j.core.state.configGetFromDict("myconfig", "namespace", "default")
    config_key = None

    if backend == "db" :
        config_key_path = j.sal.fs.joinPaths(j.dirs.HOMEDIR, "configmgrsandboxes", namespace_in_cfg, "keys", "key")
        if j.sal.fs.exists(config_key_path):
            config_key = config_key_path
    return config_key


@server.command()
@click.option('--listen', '-L', help='listen address (default :6600)', default=':6600')
@click.option('--data-repo', '-D', required=False, help='URL of the git repository or absolute path where to save the data of the zero robot')
@click.option('--template-repo', '-T', multiple=True, help='list of template repository URL. Use fragment URL to specify a branch: http://github.com/account/repo#branch')
@click.option('--config-repo', '-C', required=False, help='URL of the configuration repository (https://github.com/threefoldech/jumpscale_core/blob/development/docs/config/configmanager.md)')
@click.option('--config-key', '-K', required=False, help='Absolute path to ssh key to secure configuration data, which is committed and pushed (see auto-push) in the configuration repo.\
 If omitted, the robot will try to use the key configured key in jumpscale if any or will generate a new ssh key.')
@click.option('--debug', help='enable debug logging', is_flag=True, default=False)
@click.option('--telegram-bot-token', help='Bot to push template action failures', required=False)
@click.option('--telegram-chat-id', help='Chat id to push template action failures', required=False)
@click.option('--auto-push', help='enable automatically commit and pushing of data repository', is_flag=True, default=False)
@click.option('--auto-push-interval', help='interval in minutes of automatic pushing of data repository', required=False, default=60)
@click.option('--admin-organization', help='if specified, use this organization to protect the admin API endpoint.', required=False)
@click.option('--user-organization', help='if specified, use this organization to protect the user API endpoint.', required=False)
@click.option('--mode', help='mode of 0-robot', type=click.Choice(['node']), required=False)
@click.option('--god', help='enable god mode (use ONLY for development !!)', required=False, default=False, is_flag=True)
def start(listen, data_repo, template_repo, config_repo, config_key, debug,
          telegram_bot_token, telegram_chat_id,
          auto_push, auto_push_interval,
          admin_organization, user_organization, mode, god):
    """
    start the 0-robot daemon.
    this will start the REST API on address and port specified by --listen and block
    """
    level = "INFO"
    if debug:
        level = "DEBUG"

    j.logger.handlers_level_set(level)
    j.logger.loggers_level_set(level)

    # Check if configmanager is configured to zdb backend and has a namespace configured
    if  j.core.state.configGetFromDict("myconfig", "backend", "file") == "db":
        namespace =  j.core.state.configGetFromDict("myconfig", "namespace", "default")
        if namespace:
            j.tools.configmanager.set_namespace(namespace)
        else:
            raise RuntimeError("Working in zdb backend mode and don't have a namespace")



    if (telegram_bot_token and not telegram_chat_id) or (telegram_chat_id and not telegram_bot_token):
        raise ValueError("To enable telegram error logging, you need to specify both the --telegram-bot-token and the --telegram-chat-id options")

    if telegram_bot_token:
        telegram_logger.disabled = False
        telegrambot = j.clients.telegram_bot.get(instance='errorbot', data=dict(bot_token_=telegram_bot_token))
        handler = TelegramHandler(telegrambot, telegram_chat_id)
        handler.setFormatter(TelegramFormatter())
        handler.setLevel(logging.ERROR)
        telegram_logger.addHandler(handler)

    robot = Robot()

    for url in template_repo:
        robot.add_template_repo(url)

    robot.set_data_repo(data_repo)

    config_repo = config_repo or get_db_config_repo()
    config_key = config_key or get_db_config_key()

    robot.set_config_repo(config_repo, config_key)

    robot.start(listen=listen,
                auto_push=auto_push,
                auto_push_interval=auto_push_interval,
                admin_organization=admin_organization,
                user_organization=user_organization,
                mode=mode,
                god=god)
