#!/bin/bash
set -e

mkdir -p $HOME/code/github/threefoldtech
sudo chown -R $USER:$USER $HOME/code/github/threefoldtech
cp -r . $HOME/code/github/threefoldtech/0-robot

pushd $HOME/code/github/threefoldtech/0-robot
pip3 install -e .
popd


