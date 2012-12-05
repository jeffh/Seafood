import os
import sys

from fabric.api import local, sudo, task

from bootstrapper import lowlevel
from bootstrapper.helpers import puts, has, runner

############################# HIGH-LEVEL FUNCTIONS ##############################
@task
def setup_master(and_minion=1, upgrade=0):
    """Bootstraps and sets up a master.

    Sets up a minion pointing to itself unless otherwise said.
    """
    lowlevel.bootstrap(upgrade)
    lowlevel.master()
    lowlevel.upload()
    if int(and_minion):
        priv_key, pub_key = lowlevel.generate_minion_key(lowlevel.hostname())
        lowlevel.minion(master='127.0.0.1', pub_key=pub_key, priv_key=priv_key)


@task
def setup_minion(master, upgrade=0, pub_key=None, priv_key=None):
    "Bootstraps and sets up a minion."
    lowlevel.bootstrap(upgrade)
    lowlevel.minion(master, pub_key=pub_key, priv_key=priv_key)
    local('rm -f %s %s' % (pub_key, priv_key))


@task
def setup_minion_for_master(master_cmd, master_ip, upgrade=0):
    """Gets a key from the given master and use it to setup a minion to
    point to that master.

    master_cmd: the method to connect to master from this machine (any valid fabric command)
    master_ip: the address for the minion to connect to the master
    upgrade: whether or not to update existing packages for the minion
    
    ex: fab setup_minion_for_master:deploy_host,192.168.1.119
    """
    host = lowlevel.hostname()
    runner.action("Set up minion ({0}) for master ({1})".format(repr(host), repr(master_ip)))
    local('fab {0} lowlevel.generate_minion_key:{1}'.format(master_cmd, host))
    setup_minion(master_ip, upgrade, 'minion.pub', 'minion.pem')


@task
def deploy(filter='*', upload=1, debug=0):
    """Tells master to send pillars and execute salt state files on clients.

    If debug is set to true, runs locally with more debugging information output.
    If upload is set to true, then uploads current salt configurations to the master before deploying.
    """
    runner.action('Deploying salt files')
    output = ''
    with runner.with_prefix('  '):
        if has('/opt/saltstack/', 'test -e %(app)s'):
            lowlevel.upgrade_bleeding()
        if int(upload):
            lowlevel.upload()
        if int(debug):
            cmd = "salt-call state.highstate -l debug"
        else:    
            cmd = "salt '{0}' state.highstate".format(filter)
        output = runner.sudo(cmd, combine_stderr=True, stdout=sys.stdout)

