#!/bin/bash

# stop on failed command
set -e

GITURL=https://github.com/saltstack/salt
PIP=/usr/local/bin/pip

usage()
{
    cat << EOF
usage: $0 OPTIONS

This script to setup salt master / minion in osx.

OPTIONS:
   -h      This help
   -M      Install the master
   -S      Install the syndicate
   -N      DO NOT install the minion
   -U      DO NOT upgrade repositories first (doesn't work)
EOF
}

MASTER=
SYNDICATE=
MINION=1
UPGRADE=1
VERSION=stable
GITREF=develop
while getopts “hMSNU” OPTION
do
     case $OPTION in
         h)
             usage
             exit 1
             ;;
         M)
             MASTER=1
             shift
             ;;
         S)
             SYNDICATE=1
             shift
             ;;
         N)
             MINION=
             shift
             ;;
         U)
             UPGRADE=
             shift
             ;;
         ?)
             usage
             exit
             ;;
     esac
done
if [ "$1" ]; then
    VERSION=$1
    shift
fi
if [ "$VERSION" == "git" ]; then
    GITREF=$1
    shift
fi

function install_cltools {
    install_dmg 'Command Line Tools (Mountain Lion).mpkg'
    hdiutil mount 'xcode462_cltools_10_86938259a.dmg'
    volume="/Volumes/Command Line Tools (Mountain Lion)"
    installer -pkg "$volume/Command Line Tools (Mountain Lion).mpkg" -target /
    hdiutil detach "$volume"
}

function install_homebrew {
    rm -rf /tmp/homebrew
    git clone https://github.com/mxcl/homebrew /tmp/homebrew
    (
        cd /usr/local/
        git clean -fd
    )
    chmod -R 755 /usr/local/
    chown -R root /usr/local/
    chgrp -R staff /usr/local/
}

function install_dependencies {
    # salt requires these directories... not sure why
    mkdir -p /var/cache/salt/master; true
    mkdir -p /var/cache/salt/minion; true

    brew install swig
    brew install zmq
    brew install python
}

function setup_salt {
    if [ "$VERSION" == "stable" ]; then
        $PIP install salt
    elif [ "$VERSION" == "develop"]; then
        $PIP install "git+${GITURL}#egg=salt"
    elif [ "$GITREF" ]; then
        $PIP install "git+${GITURL}#egg=salt"
    fi

    # increase max file descriptor limit
    launchctl limit maxfiles 10000

    export PATH=$PATH:/usr/local/share/python/ > ~/.bash_profile
}

function setup_master {
    filepath='/Library/LaunchDaemons/org.saltstack.salt-master.plist'
    cp -f org.saltstack.salt-master.plist $filepath
    chown root $filepath
    chgrp wheel $filepath
    launchctl load -w $filepath
}

function setup_minion {
    filepath='/Library/LaunchDaemons/org.saltstack.salt-minion.plist'
    cp -f org.saltstack.salt-minion.plist $filepath
    chown root $filepath
    chgrp wheel $filepath
    launchctl load -w $filepath
}

function main {
    install_cltools
    install_homebrew
    setup_salt
    if [ "$MASTER" ]; then
        setup_master
    fi
    if [ "$MINION" ]; then
        setup_minion
    fi
}

main

