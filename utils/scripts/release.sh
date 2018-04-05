#!/bin/bash

VERSION=$1
JS_REVISION=$2

echo "creation release for $VERSION (js:$JS_REVISION)"

echo "update jumpscale revision"
sed -i "s/development/$JS_REVISION/g" utils/scripts/autobuild/flist.sh
sed -i "s/development/$JS_REVISION/g" utils/scripts/autobuild/flist_autostart.sh

echo "set release flist in 0-robot auto start script"
sed  -i "/root =/c\root = \"https://hub.gig.tech/gig-autobuilder/zero-os-0-robot-autostart-$VERSION.flist\"" utils/scripts/autobuild/node_startup.toml

echo "bump 0-robot version"
sed -i "/version=/c\    version='$VERSION'," setup.py
