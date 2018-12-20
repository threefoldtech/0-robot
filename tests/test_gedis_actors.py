import os

import gevent
import pytest
from Jumpscale import j
from zerorobot import config, gedis
from zerorobot import service_collection as scol
from zerorobot import storage
from zerorobot import template_collection as tcol
from zerorobot import webhooks
from zerorobot.server.auth import user_jwt


class ActorTestBase:

    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        # configure the server
        cls.server = j.servers.gedis.configure(instance='test', port=8889, host='0.0.0.0', ssl=False, adminsecret='')
        # load a single actor
        for filename in ['templates.py', 'robot.py', 'services.py']:
            actor_path = os.path.join(os.path.dirname(gedis.__file__), filename)
            cls.server.actor_add(actor_path, namespace='test')
        gevent.spawn(cls.server.start)
        cls.client = j.clients.gedis.configure(instance='test', host='127.0.0.1',
                                               port=8889, namespace='test', ssl=False, reset=True)

        tcol.add_repo('http://github.com/threefoldtech/0-robot', directory='tests/fixtures/templates')

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        cls.server.stop()

    def setup(self):
        config.config_repo = config.ConfigRepo(j.sal.fs.getTmpDirPath())
        config.data_repo = config.DataRepo(j.sal.fs.getTmpDirPath())
        config.webhooks = webhooks.get(config)
        storage.init(config)

    def teardown(self):
        scol.drop_all()


class TestRobotActor(ActorTestBase):

    def test_info(self):
        info = self.client.robot.info()
        assert info is not None
        assert info.storage_healthy is True

    def test_metrics(self):
        metrics = self.client.robot.metrics()
        assert metrics is not None

    def test_webhook_add(self):
        webhook = j.data.schema.get(url='zrobot.webhook').new()
        webhook.url = 'http://webhook.com/'
        webhook.kind = 'eco'
        result = self.client.robot.webhook_add(webhook)
        assert result.url == webhook.url
        assert result.kind == webhook.kind

    def test_webhook_list(self):
        result = self.client.robot.webhook_list()
        assert isinstance(result, list)
        assert len(result) == 0

        config.webhooks.add('http://webhooks.com', 'eco')
        result = self.client.robot.webhook_list()
        schema = j.data.schema.get(url='zrobot.webhook')
        assert len(result) == 1
        webhook = schema.get(capnpbin=result[0])
        assert webhook.url == 'http://webhooks.com'
        assert webhook.kind == 'eco'
        assert webhook.guid

    def test_webhook_delete(self):
        self.client.robot.webhook_delete()

        wh1 = config.webhooks.add('http://webhooks.com', 'eco')
        wh2 = config.webhooks.add('http://webhooks2.com', 'eco')

        assert True == self.client.robot.webhook_delete(wh1.id)
        assert len(list(config.webhooks.list())) == 1


class TestTemplateActor(ActorTestBase):

    def test_template_list(self):
        assert 6 == len(self.client.templates.list())

    def test_template_add(self, mocker):
        # avoid side effect of downloading repos
        add_repo_mocked = mocker.patch('zerorobot.template_collection.add_repo')

        repository = j.data.schema.get(url='zrobot.template_repository').new()
        repository.url = 'http://threefoldtech/0-templaplates'
        repository.branch = 'master'
        self.client.templates.add(repository)

    def test_template_checkout(self, mocker):
        # avoid side effect of downloading repos
        add_repo_mocked = mocker.patch('zerorobot.template_collection.checkout_repo')
        repository = j.data.schema.get(url='zrobot.template_repository').new()
        repository.url = 'http://threefoldtech/0-templaplates'
        repository.branch = 'other'
        assert b'OK' == self.client.templates.checkout(repository)


class TestServiceActor(ActorTestBase):

    def load_template(self, name):
        """
        name of the template to load from the
        fixtures/templates folder
        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        tmpl = tcol._load_template("https://github.com/threefoldtech/0-robot",
                                   os.path.join(dir_path, 'fixtures', 'templates', name))
        return tmpl

    def test_service_list(self):
        assert len(self.client.services.list(secrets=[])) == 0

        Node = self.load_template('node')
        expected_service = tcol.instantiate_service(Node, 'testnode')
        expected_service.state.set('actions', 'install', 'ok')
        expected_service.state.set('actions', 'start', 'ok')
        expected_service.state.set('status', 'running', 'ok')
        secret = user_jwt.create({'service_guid': expected_service.guid})

        services = self.client.services.list(secrets=[secret])
        assert len(services) == 1
        # TODO: fix when listing of object is working in gedis
        actual_service = j.data.schema.get(url='zrobot.service').get(capnpbin=services[0])
        assert actual_service.name == expected_service.name
        assert actual_service.guid == expected_service.guid
        assert actual_service.template == str(expected_service.template_uid)
        assert actual_service.version == expected_service.version
        assert len(actual_service.state) == 3

    def test_service_create(self):
        service = j.data.schema.get(url='zrobot.service').new()
        service.template = 'node'
        service.name = 'test'
        service.data = j.data.serializers.msgpack.dumps({'ip': '192.168.10.1', 'port': 22})

        result = self.client.services.create(service)
        assert result.guid
        assert result.template == 'github.com/threefoldtech/0-robot/node/0.0.1'
        assert result.name == 'test'
        assert result.secret
        assert result.public is False

    def test_service_get(self):
        Node = self.load_template('node')
        expected_service = tcol.instantiate_service(Node, 'testnode')

        secret = user_jwt.create({'service_guid': expected_service.guid})
        service = self.client.services.get(expected_service.guid, [secret])
        assert service.name == expected_service.name
        assert service.guid == expected_service.guid
        assert service.template == str(expected_service.template_uid)
        assert service.version == expected_service.version

        # valid guid but no sercret
        with pytest.raises(Exception):  # TODO: catch proper exception
            self.client.services.get('notexits', [])

        # invalid guid
        with pytest.raises(Exception):  # TODO: catch proper exception
            self.client.services.get('notexits', [secret])

    def test_service_delete(self):
        self.client.services.delete('notexists', )

        Node = self.load_template('node')
        service = tcol.instantiate_service(Node, 'testnode')
        assert scol.get_by_guid(service.guid)  # ensure it exists

        secret = user_jwt.create({'service_guid': service.guid})
        self.client.services.delete(service.guid, [secret])

        with pytest.raises(scol.ServiceNotFoundError):
            scol.get_by_guid(service.guid)  # ensure it's been deleted

    def test_service_actions(self):
        Node = self.load_template('node')
        service = tcol.instantiate_service(Node, 'testnode')
        assert scol.get_by_guid(service.guid)  # ensure it exists
        secret = user_jwt.create({'service_guid': service.guid})

        actions = self.client.services.actions(service.guid, [secret])
        assert len(actions) == 10
        schema = j.data.schema.get(url='zrobot.action')
        for action in actions:
            action = schema.get(capnpbin=action)

    def test_service_tasks(self):
        Node = self.load_template('node')
        service = tcol.instantiate_service(Node, 'testnode')
        assert scol.get_by_guid(service.guid)  # ensure it exists
        secret = user_jwt.create({'service_guid': service.guid})

        for action in ['start', 'stop', 'error']:
            service.schedule_action(action)

        result = self.client.services.tasks(guid=service.guid, secrets=[secret], all=True)
        task_schema = j.data.schema.get(url='zrobot.task')
        tasks = []
        for item in result:
            tasks.append(task_schema.get(capnpbin=item))

        assert len(tasks) == 3

    def test_service_task_create(self):
        Node = self.load_template('node')
        service = tcol.instantiate_service(Node, 'testnode')
        assert scol.get_by_guid(service.guid)  # ensure it exists
        secret = user_jwt.create({'service_guid': service.guid})

        for action in ['start', 'stop', 'error']:
            service.schedule_action(action)

        task = j.data.schema.get(url='zrobot.task').new()
        task.action_name = 'start'

        result = self.client.services.task_create(guid=service.guid, secrets=[secret], task=task)
        assert result.action_name == 'start'
        assert result.state == 'new'
        assert result.guid

    def test_service_logs(self):
        Node = self.load_template('node')
        service = tcol.instantiate_service(Node, 'testnode')
        assert scol.get_by_guid(service.guid)  # ensure it exists
        secret = user_jwt.create({'service_guid': service.guid})

        result = self.client.services.logs(guid=service.guid, secrets=[secret])
        assert result.logs == ""
