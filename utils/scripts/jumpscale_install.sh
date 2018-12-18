#!/bin/bash
set -e

# settings

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/jumpscale_versions.sh"

for target in /usr/local $HOME/code $HOME/code/github/threefoldtech $HOME/opt $HOME/opt/cfg $HOME/opt/var/capnp $HOME/opt/var/log $HOME/jumpscale/cfg; do
    mkdir -p $target
    sudo chown -R $USER:$USER $target
done


pushd $HOME/code/github/threefoldtech

# cloning source code
for target in jumpscale_core jumpscale_lib jumpscale_prefab; do
    git clone https://github.com/threefoldtech/${target}
    pushd ${target}
    x=${target}_revision
    git checkout ${!x}
    popd
done

# install jumpscale
for target in jumpscale_core jumpscale_lib jumpscale_prefab; do
    pushd ${target}
    pip3 install -e .
    popd
done

popd


# create ssh key for jumpscale config manager
mkdir -p ~/.ssh
ssh-keygen -f ~/.ssh/id_rsa -P ''
eval `ssh-agent -s`
ssh-add ~/.ssh/id_rsa

# initialize jumpscale config manager
mkdir -p $HOME/code/config_test
git init $HOME/code/config_test
touch $HOME/code/config_test/.jsconfig
js_config init --silent --path $HOME/code/config_test/ --key ~/.ssh/id_rsa