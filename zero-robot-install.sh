#!/bin/sh

# so this script basically pre-installs as much as possible so that
# pip, which is... um... a good way to bypass distro-released python
# packages shall we say... doesn't get a word in edgeways unless
# absolutely, absolutely necessary.  and even then it's dodgy.
#
# the only dodgy one which absolutely had to be brought in was
# pycapnp, which had to be forced into using a specific version
# of libcapnp... which *should* still have worked... but doesn't
# build.  yay.
#
# the script can be re-run without needing to "blow away" pre-existing
# dependencies and work.  git repositories that were previously downloaded
# successfully will have a "git pull" done in them, instead.


# hack to stop jumpscale_lib from force-installing electrum
monkey_patch_path_for_overloading_pip3() {
	mkdir -p hack_bin
	PATH=`pwd`/hack_bin:$PATH
	export $PATH
	cat <<EOF >>hack_bin/pip3
#!/bin/sh
echo pip3 dummy, stops jumpscale_lib from running forced install of electrum
EOF
	chmod a+x hack_bin/pip3
}

# checks out / pulls a specific version of a git branch
# runs python install
python_git_repo_v() {
 
    echo "installing" into $2, $1
    if [ ! -d $2 ]; then
        git clone $1
    else
        cd $2
        git pull
        cd ..
    fi
    cd $2
    git checkout $3
    python3 setup.py install
    cd ..
}

# checks out / pulls the default version of a git branch
# runs python install
python_git_repo() {
 
    echo "installing" into $2, $1
    if [ ! -d $2 ]; then
        git clone $1
    else
        cd $2
        git pull
        cd ..
    fi
    cd $2
    python3 setup.py install $3
    cd ..
}

mk_hack_symlink () {
    # jaezuss, this is truly dreadful, the way that installs fail if the
    # symlinks don't exist...

    TFT=/opt/code/github/threefoldtech
    mkdir -p $TFT
    if [ ! -L "$TFT/$1" ]; then
        ln -s `pwd`/$1 $TFT
    fi
}

# looots of python package dependencies...
apt-get update
apt-get install -y build-essential git python3
apt-get install -y python3-setuptools
apt-get install -y python3-colorlog
apt-get install -y python3-psutil
apt-get install -y python3-pytoml
apt-get install -y python3-pystache
apt-get install -y lsb_release
apt-get install -y sudo
apt-get install -y python3-redis python3-fakeredis
apt-get install -y build-essential
apt-get install -y python3-dev
apt-get install -y libssh-dev
apt-get install -y libssh2-dev
apt-get install -y libsssh2-1-dev
apt-get install -y libssh2-1-dev
apt-get install -y python-libssh2
apt-get install -y python3-paramiko
apt-get install -y python-libssh2
apt-get install -y python3-gevent
apt-get install -y python3-pygments
apt-get install -y python3-libtmux
apt-get install -y python3-rsa
apt-get install -y python3-future
apt-get install -y python3-click
apt-get install -y python3-flask
apt-get install -y python3-prometheus-client
apt-get install -y python3-netifaces
apt-get install -y python3-jsonschema
apt-get install -y python3-yaml
apt-get install -y python3-requests
apt-get install -y python3-msgpack
apt-get install -y python3-git
apt-get install -y python3-netaddr
apt-get install -y cython3
apt-get install -y libcapnp-dev
apt-get install -y python3-unidecode
apt-get install -y lsb-release
#apt-get install -y pssh

# for testing
apt-get install -y python3-serial
apt-get install -y python3-msgpack
apt-get install -y python3-watchdog
apt-get install -y python3-future
apt-get install -y python3-pytoml
apt-get install -y python3-toml
apt-get install -y python3-dateutil
apt-get install -y python3-ipython
apt-get install -y python3-httplib2
apt-get install -y python3-jedi

# lots of python packages that aren't packaged in debian...
python_git_repo https://github.com/capnproto/pycapnp.git pycapnp \
                                        --force-bundled-libcapnp

python_git_repo https://github.com/ParallelSSH/parallel-ssh parallel-ssh
python_git_repo https://github.com/staticshock/colored-traceback.py \
                                               colored-traceback.py

python_git_repo https://github.com/npcole/npyscreen.git npyscreen
python_git_repo https://github.com/jaraco/path.py.git path.py
python_git_repo https://github.com/mpdavis/python-jose.git python-jose
python_git_repo https://github.com/trezor/python-mnemonic.git python-mnemonic

# electrum 3.2.2 is a critical dependency of jumpscale_lib ??? moo???
apt-get install -y python3-qrcode
apt-get install -y python3-pyaes
apt-get install -y python3-protobuf
apt-get install -y python3-jsonrpclib-pelix
apt-get install -y python3-dnspython
apt-get install -y python3-ecdsa
apt-get install -y python3-pbkdf2
apt-get install -y python3-socks
apt-get install -y python3-requests
python_git_repo_v https://github.com/spesmilo/electrum.git electrum 3.2.2

# TODO....
#ays9/.git/config:	url = https://github.com/jumpscale/ays9
#core9/.git/config:	url = https://github.com/threefoldtech/jumpscale_core
#home/.git/config:	url = https://github.com/jumpscale/home
#jumpscale_core/.git/config:	url = https://github.com/threefoldtech/jumpscale_core
#portal9/.git/config:	url = https://github.com/jumpscale/portal9

# these allow jumpscale_core to "pick up" locations that need to be walked
# in order to create the jumpscale.py file, which is then installed
# (now using distutils setup).
mk_hack_symlink jumpscale_lib
mk_hack_symlink jumpscale_prefab
mk_hack_symlink jumpscale_core

# grab the three main jumpscale repos...
python_git_repo https://github.com/threefoldtech/jumpscale_core jumpscale_core
python_git_repo https://github.com/threefoldtech/jumpscale_lib jumpscale_lib
python_git_repo https://github.com/threefoldtech/jumpscale_prefab \
                                                    jumpscale_prefab

# now... at last... finally...
mk_hack_symlink 0-robot
python_git_repo https://github.com/threefoldtech/0-robot 0-robot
