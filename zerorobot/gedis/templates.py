from Jumpscale import j
from zerorobot import template_collection as tcol
from zerorobot.server.handlers.views import template_view

JSBASE = j.application.JSBaseClass


class templates(JSBASE):

    def __init__(self):
        super().__init__()

    def list(self):
        # TODO: fix once gedis support list of objects
        # ```out
        # (LO)!zrobot.template
        # ```
        schema = j.data.schema.get(url='zrobot.template')
        output = []
        for template in tcol.list_templates():
            output.append(schema.get(data=template_view(template))._data)

        return output

    def add(self, repository):
        """
        ```in
        repository = (O)!zrobot.template_repository
        ```
        """
        # TODO: fix once gedis support list of objects
        # ```out
        # (LO)!zrobot.template
        # ```
        branch = 'master'
        if repository.branch:
            branch = repository.branch
        added = tcol.add_repo(repository.url, branch=branch)

        schema = j.data.schema.get(url='zrobot.template')
        output = []
        for template in added:
            output.append(schema.get(data=template_view(template))._data)

        return output

    def checkout(self, repository):
        """
        ```in
        repository = (O)!zrobot.template_repository
        ```
        """
        tcol.checkout_repo(repository.url, repository.branch)
        return "OK"
