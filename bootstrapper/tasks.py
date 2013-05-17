import os
import sys
import time

from fabric.api import local, sudo, parallel, show, env, task
from fabric.api import roles as _roles
from fabric.api import reboot as _reboot
from fabric.contrib import files

from bootstrapper import lowlevel
from bootstrapper.helpers import (puts, has, requires_configuration,
    requires_host, boolean, service, copy)
from bootstrapper.lowlevel.utils import log_to_file, print_line

# expose this task
hostname = task(lowlevel.hostname)

############################# HIGH-LEVEL FUNCTIONS ##############################
@parallel
@requires_host
def delete_salt():
    return lowlevel.purge_salt()

@task
@parallel
@requires_host
def reboot():
    print_line("Rebooting")
    _reboot()
    print_line("Done")

@task
@log_to_file('setup_master.log')
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
    print_line("-> Bootstrapping master")
    lowlevel.bootstrap(master=True, minion=and_minion, upgrade=upgrade)
    print_line("-> Configuring salt master")
    lowlevel.master()
    print_line("-> Syncing salt data")
    lowlevel.upload(sync=False)
    if boolean(and_minion):
        print_line("-> Configuring salt minion")
        name = hostname()
        roles = ['salt-master'] + list(env.salt_roles)
        lowlevel.create_minion_key(name)
        lowlevel.minion(master='127.0.0.1', hostname=name, roles=roles)

    if env.salt_bleeding:
        print_line("-> Converting salt to bleeding edge")
        lowlevel.convert_to_bleeding()
        time.sleep(1)
        if boolean(and_minion):
            service('salt-minion', 'start')
        service('salt-master', 'start')


@task
@log_to_file('create_minion_key.log')
@_roles('master')
@requires_host
def create_minion_key(hostname):
    "Creates a minion key from the master and downloads it"
    lowlevel.create_minion_key(hostname)


@task
@log_to_file('setup_minion.log')
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
    print_line("-> Bootstrapping minion")
    name = hostname()
    lowlevel.bootstrap(master=False, minion=True, upgrade=upgrade)
    print_line("-> Generating minion key")
    local('fab {0} create_minion_key:{1}'.format(fab_master, repr(name)))
    lowlevel.minion(master, name, env.salt_roles)

    if env.salt_bleeding:
        print_line("-> Converting salt to bleeding edge")
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
    return sudo("salt {0!r} test.version".format(filter))

@task
@log_to_file('deploy.log')
@requires_host
@requires_configuration
def deploy(filter='*', upload=1, sync=1, debug=0):
    """Tells master to send pillars and execute salt state files on clients.

    If debug is set to 'yes', runs locally with more debugging information output.
    If upload is set to 'yes', then uploads current salt configurations to the master before deploying.
    """
    print_line("-> Displaying salt versions")
    print_line(salt_versions(filter))
    if boolean(upload):
        print_line("-> Uploading & syncing salt data files")
        lowlevel.upload()
    if boolean(sync):
        print_line("-> Running highstate")
        if boolean(debug):
            cmd = "salt-call state.highstate -l debug"
        else:
            cmd = "salt {0!r} state.highstate".format(filter)
        with show('stdout', 'stderr'):
            out = sudo(cmd, combine_stderr=True)
            print_line(out)

