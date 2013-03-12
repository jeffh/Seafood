import os
import sys
import time

from fabric.api import local, sudo, task, parallel, show, env
from fabric.api import roles as _roles
from fabric.api import reboot as _reboot
from fabric.contrib import files

from bootstrapper import lowlevel
from bootstrapper.helpers import (puts, has, requires_configuration,
    requires_host, boolean, service, copy)

# expose this task
hostname = lowlevel.hostname

############################# HIGH-LEVEL FUNCTIONS ##############################
@task
@parallel
@requires_host
def delete_salt():
    return lowlevel.purge_salt()

@task
@parallel
@requires_host
def reboot():
    print "Rebooting"
    _reboot()
    print "Done"

@task
@_roles('master')
@requires_host
@requires_configuration
def setup_master(and_minion=1, upgrade=0):
    """Bootstraps and sets up a master.

    Sets up a minion pointing to itself unless otherwise said.

    Options:
        and_minion: Set to 'no' to not install salt-minion.
        upgrade:    Set to 'yes' to upgrade all system packages before
                    installing salt.
    """
    lowlevel.bootstrap(master=True, minion=and_minion, upgrade=upgrade)
    lowlevel.master()
    lowlevel.upload(sync=False)
    if boolean(and_minion):
        name = hostname()
        roles = ['salt-master'] + list(env.salt_roles)
        lowlevel.create_minion_key(name)
        lowlevel.minion(master='127.0.0.1', hostname=name, roles=roles)
    
    
    if env.salt_bleeding:
        lowlevel.convert_to_bleeding()
        time.sleep(1)
        if boolean(and_minion):
            service('salt-minion', 'start')
        service('salt-master', 'start')


@task
@_roles('master')
@requires_host
def create_minion_key(hostname):
    "Creates a minion key from the master and downloads it"
    lowlevel.create_minion_key(hostname)


@task
@_roles('minion')
@requires_host
def setup_minion(fab_master, master, upgrade=0):
    """Bootstraps and sets up a minion. Requires the ip address of the master.
    
    Options:
        fab_master: The method for this machine (running fabric) to connect to the
                    master. This can be specified as "-H <IPADDRESS>" or fabric
                    task name
        master:     The address for the minion to connect to the master.
        upgrade:    Set to 'yes' to upgrade all the minion's packages before
                    installing salt-minion
    """
    name = hostname()
    lowlevel.bootstrap(master=False, minion=True, upgrade=upgrade)
    local('fab {0} create_minion_key:{1}'.format(fab_master, repr(name)))
    lowlevel.minion(master, name, env.salt_roles)

    if env.salt_bleeding:
        lowlevel.convert_to_bleeding()
        time.sleep(1)
        service('salt-minion', 'start')

@task
@_roles('master')
@requires_host
def master_logs():
    "Prints out all the logs from the salt master"
    sudo('cat /var/log/salt/master')

@task
@requires_host
def minion_logs():
    "Prints out all the logs from ths salt minion"
    sudo('cat /var/log/salt/minion')

@task
@_roles('master')
@requires_host
def salt_versions(filter='*'):
    sudo('salt --version')
    sudo("salt {0!r} test.version".format(filter))

@task
@requires_host
@requires_configuration
def deploy(filter='*', upload=1, sync=1, debug=0):
    """Tells master to send pillars and execute salt state files on clients.

    If debug is set to 'yes', runs locally with more debugging information output.
    If upload is set to 'yes', then uploads current salt configurations to the master before deploying.
    """
    print 'Deploying salt files'
    print '======== Minions ========'
    salt_versions(filter)
    if boolean(upload):
        lowlevel.upload()
    if boolean(sync):
        if boolean(debug):
            cmd = "salt-call state.highstate -l debug"
        else:
            cmd = "salt {0!r} state.highstate".format(filter)
        print 'Ensuring minion state'
        with show('stdout', 'stderr'):
            out = sudo(cmd, combine_stderr=True)
        with open('sync.log', 'w+') as handle:
            handle.write(out)
        print 'Wrote output to sync.log'

