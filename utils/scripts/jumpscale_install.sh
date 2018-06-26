#!/bin/bash
set -e

# settings

export CORE_REVISION="c76a0f192050b3d518fb28a71848a1421472755d"
export LIB_REVISION="37a73e932da2c0da57511e8cb8563c5b9f76002e"
export PREFAB_REVISION="8cd3d2a7a8e15e8b9aa3ec7b3d6965e13b85e060"

for target in /usr/local /opt /opt/cfg /opt/code/github/jumpscale /opt/var/capnp /opt/var/log $HOME/js9host/cfg; do
    mkdir -p $target
    sudo chown -R $USER:$USER $target
done


pushd /opt/code/github/jumpscale

# cloning source code
git clone https://github.com/jumpscale/core9
pushd core9
git checkout $CORE_REVISION
popd

git clone https://github.com/jumpscale/lib9
pushd lib9
git checkout $LIB_REVISION
popd

git clone https://github.com/jumpscale/prefab9
pushd prefab9
git checkout $PREFAB_REVISION
popd

# installing core and plugins
for target in core9 lib9; do
    pushd ${target}
    pip3 install .
    popd
done
popd


# create ssh key for jumpscale config manager
mkdir -p ~/.ssh
ssh-keygen -f ~/.ssh/id_rsa -P ''
eval `ssh-agent -s`
ssh-add ~/.ssh/id_rsa

# initialize jumpscale config manager
mkdir -p /opt/code/config_test
git init /opt/code/config_test
touch /opt/code/config_test/.jsconfig
js9_config init --silent --path /opt/code/config_test/ --key ~/.ssh/id_rsa