#!/usr/bin/python3
import os
import time
from js9 import j

if not j.sal.fs.exists("/root/.ssh/id_rsa"):
    j.tools.prefab.local.system.ssh.keygen(user='root', name='id_rsa')
    print("Configure the following ssh public key to have write access to your config / data repository:\n%s" % pubkey)
    exit(0)

j.tools.prefab.local.core.run("js9_config init -s -k /root/.ssh/id_rsa")

cmd_line = "zrobot server start"
args = [
    "listen", 
    "data-repo", 
    "template-repo", 
    "config-repo", 
    "debug", 
    "telegram-bot-token", 
    "telegram-chat-id", 
    "auto-push", 
    "auto-push-interval"
]
for arg in args:
    val = os.environ.get(arg)
    if val:
        if arg in ("debug", "auto-push"):
            cmd_line += " --%s" % arg
        else:
            cmd_line += " --%s '%s'" % (arg, val.replace("'", "\\'"))

j.tools.prefab.local.core.run(cmd_line)