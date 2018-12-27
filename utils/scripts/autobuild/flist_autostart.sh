#!/bin/bash
set -ex

# make output directory
ARCHIVE=/tmp/archives
FLIST=/tmp/flist
mkdir -p $ARCHIVE

# install system deps
apt-get update
apt-get install -y locales git sudo python3-pip libffi-dev python3-dev libssl-dev libpython3-dev libssh-dev libsnappy-dev build-essential pkg-config libvirt-dev libsqlite3-dev ipmitool iputils-ping cmake  -y

# setting up locales
if ! grep -q ^en_US /etc/locale.gen; then
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
    locale-gen
fi

for target in /usr/local $HOME/code $HOME/code/github/threefoldtech $HOME/opt $HOME/opt/cfg $HOME/opt/var/capnp $HOME/opt/var/log $HOME/jumpscale/cfg; do
    mkdir -p $target
    sudo chown -R $USER:$USER $target
done

# install jumpscale
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/../jumpscale_versions.sh"

pushd $HOME/code/github/threefoldtech

# cloning source code
for target in jumpscale_core jumpscale_lib jumpscale_prefab digital_me; do
    git clone https://github.com/threefoldtech/${target}
    pushd ${target}
    x=${target}_revision
    git checkout ${!x}
    popd
done

# install jumpscale
for target in jumpscale_core jumpscale_lib jumpscale_prefab digital_me; do
    pushd ${target}
    pip3 install -e .
    popd
done

popd


cp -r /0-robot $HOME/code/github/threefoldtech
# install 0-robot
pushd $HOME/code/github/threefoldtech/0-robot
pip3 install -e .
cp utils/scripts/autobuild/startup.toml /.startup.toml
cp utils/scripts/autobuild/startup.py /.startup.py
popd

echo '# DNS unset during autobuild of 0-robot' > /etc/resolv.conf

tar -cpzf "/tmp/archives/0-robot-autostart.tar.gz" --exclude tmp --exclude dev --exclude sys --exclude proc  /
