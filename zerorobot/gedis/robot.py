from Jumpscale import j
from zerorobot import config
from zerorobot import service_collection as scol
from zerorobot import storage
from zerorobot.prometheus.host.linux import cpu_stat, mem_stat

JSBASE = j.application.JSBaseClass


class robot(JSBASE):

    def __init__(self):
        super().__init__()

    def info(self, schema_out):
        """
        ```out
        !zrobot.robot_info
        ```
        """
        info = schema_out.new()
        info.config_repo.url = config.config_repo.url or ""
        info.data_repo.url = config.data_repo.url or ""

        if config.data_repo.last_pushed:
            info.data_repo.last_pushed = config.data_repo.last_pushed
        if config.config_repo.last_pushed:
            info.config_repo.last_pushed = config.config_repo.last_pushed
        if config.mode:
            info.type = config.mode

        info.storage_healthy = storage.health()

        return info

    def metrics(self, schema_out):
        """
        ```out
        !zrobot.robot_metrics
        ```
        """
        metrics = schema_out.new()
        mem_active, mem_total, mem_cached, mem_free, swap_total, swap_free = mem_stat.mem_stats()
        metrics.memory.total = mem_total
        metrics.memory.active = mem_active
        metrics.memory.free = mem_free
        metrics.memory.cached = mem_cached
        metrics.memory.swap_total = swap_total
        metrics.memory.swap_free = swap_free

        cpu_stats = cpu_stat.cpu_percents()
        metrics.cpu.user = cpu_stats['user']
        metrics.cpu.nice = cpu_stats['nice']
        metrics.cpu.system = cpu_stats['system']
        metrics.cpu.idle = cpu_stats['idle']
        metrics.cpu.irq = cpu_stats['irq']
        metrics.cpu.softirq = cpu_stats['softirq']

        metrics.nr_services = len(scol.list_services())
        return metrics

    def webhook_add(self, webhook, schema_out):
        """
        ```in
        webhook = (O) !zrobot.webhook
        ```

        ```out
        !zrobot.webhook
        ```
        """
        created_webhook = config.webhooks.add(webhook.url, webhook.kind)
        result = schema_out.new()
        result.guid = created_webhook.id
        result.url = created_webhook.url
        result.kind = webhook.kind
        return result

    def webhook_list(self):
        # TODO: fix list of object in schema
        # """
        # ```out
        # schema_out = (LO) !zrobot.webhook
        # ```
        # """
        schema = j.data.schema.get(url='zrobot.webhook')
        output = []
        for wh in config.webhooks.list():
            webhook = schema.get(data=wh.as_dict())
            output.append(webhook._data)
        return output

    def webhook_delete(self, guid):
        """
        ```in
        guid = (guid)
        ```
        """
        webhooks = config.webhooks
        webhooks.delete(guid)
        return True
