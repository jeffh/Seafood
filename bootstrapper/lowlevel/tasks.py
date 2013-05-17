import os
import time

from fabric.api import (
    reboot, env, sudo, runs_once, local,
    settings, cd, run, roles, get, put
)
from fabric.contrib import files

from bootstrapper.helpers import *
from bootstrapper.config import CONFIG_DIR, SALT_DIR, master_minions_dir, minion_key_path, group
from bootstrapper.lowlevel.utils import config_template_upload, salt_config_context, set_hostname


@roles('minion')
def minion(master, hostname, roles=()):
    """Sets up the salt-minion on the remote server.
    Argument should be the ip address of the salt master.
    """
    upload_minion_key(hostname)
    upload_minion_config(master, roles)


@requires_host
def hostname(name='', fqdn=True):
    "Gets or sets the machine's hostname"
    if name:
        set_hostname(name)
    else:
        return sudo('hostname {0}'.format('-f' if boolean(fqdn) else '')).strip()



@roles('minion')
def upload_minion_key(hostname, minion_key_dir=None):
    "Installs the minion key generated from the master."
    minion_key_dir = minion_key_dir or minion_key_path()
    remove(hostname, hostname + '.pub')
    remove(hostname, hostname + '.pem')
    put(os.path.join('keys', hostname + '.pem'))
    put(os.path.join('keys', hostname + '.pub'))
    for ext in ['.pem', '.pub']:
        dest_file = os.path.join(minion_key_dir, 'minion' + ext)
        silent_remove(dest_file)
        move(hostname + ext, dest_file)
        chown('root', dest_file)
        chgrp('root', dest_file)
    chmod(400, os.path.join(minion_key_dir, 'minion.pem'))
    chmod(644, os.path.join(minion_key_dir, 'minion.pub'))


@roles('master')
def create_minion_key(hostname, key_dir=None):
    """Geneates a minion key for the given hostname. It then downloads
    the minion keys to the local keys directory for use by
    grab_minion_key.

    Must be run on the master host.
    """
    key_dir = key_dir or master_minions_dir()
    context = dict(hostname=hostname, key_dir=key_dir, user=env.user)
    sudo('salt-key --gen-keys={hostname} --gen-keys-dir={key_dir}'.format(**context))

    key_name = '{key_dir}/{hostname}'.format(**context)

    move(key_name + '.pub', key_name) # master the public key
    copy(key_name, hostname + '.pub') # copy the public key to download
    move(key_name + '.pem', hostname + '.pem') # move the private key to download
    chown(env.user, hostname + '.pem') # make sure we can download them
    chown(env.user, hostname + '.pub')
    get(hostname + '.pem', os.path.join('keys', hostname + '.pem')) # download
    get(hostname + '.pub', os.path.join('keys', hostname + '.pub'))



@roles('master')
def master():
    "Sets up the salt-master on the remote server."
    upload_master_config()


@roles('master')
def upload_master_config():
    "Uploads master config to the remote server and restarts the salt-master."
    config_template_upload('master', '/etc/salt/master', context=salt_config_context())
    service('salt-master', 'stop')
    silent_sudo('pkill salt-master') # to ensure it gets killed
    time.sleep(1)
    service('salt-master', 'start')


@roles('minion')
def upload_minion_config(master, roles=()):
    "Uploads the minion config to the remote server and restarts the salt-minion."
    print 'Upload minion configuration'
    config_template_upload('minion', '/etc/salt/minion', context=salt_config_context(roles, master=master))
    print "Restart salt-minion"
    service('salt-minion', 'stop; true')
    silent_sudo('pkill salt-minion')
    time.sleep(1)
    service('salt-minion', 'start')



@requires_configuration
def upload(sync=True):
    "Uploads all pillars, modules, and states to the remote server."
    print "Upload Salt Data"
    silent_mkdir(SALT_DIR)
    for system in env.configs:
        print "Upload configuration:", system
        for dirname in ('states', 'pillars'):
            src = os.path.join(CONFIG_DIR, system, dirname)
            path = os.path.join(SALT_DIR, system)
            dest = os.path.join(path, dirname)
            print "    - {0}/{1}".format(system, dirname)
            with settings(warn_only=True):
                mkdir(dest)
            chown(env.user, dest)
            sync_dir(src, dest, exclude=['.*'])
            chown('root', dest)
            chgrp('root', dest)
    if sync:
        salt('saltutil.refresh_pillar')
        salt('saltutil.sync_all')

