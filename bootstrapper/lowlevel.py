"""All low-level tasks that the highlevel module invokes
"""
import os
import sys
import time

from fabric.api import (reboot, env, sudo, runs_once, local,
    settings, cd, run, roles, get, put, task)
from fabric.contrib import files
from fabric import operations

from bootstrapper.helpers import *
from bootstrapper.config import CONFIG_DIR, SALT_DIR, master_minions_dir, minion_key_path, group


purge_salt = Dispatcher('purge_salt',
    dispatch=has,
    doc="Removes all salt files from the remote system"
)

bootstrap = Dispatcher('bootstrap',
    dispatch=is_platform,
    doc="Bootstraps the salt minion/master to the given host."
)

@purge_salt.register('apt-get')
def purge_salt_with_apt():
    apt_remove('salt-master', 'salt-minion', 'salt-common')
    silent_remove('/etc/salt', '/opt/salt', '/opt/saltstack', '/var/log/salt')
    silent_remove('/usr/local/bin/salt-*')


@purge_salt.before
def purge_salt_files():
    silent_remove('/etc/salt/')
    silent_remove('/opt/salt/')


@task
def upload_key(local_key='~/.ssh/id_rsa.pub'):
    "Uploads the provided local key to the remote server."
    local_key = os.path.expandvars(os.path.expanduser(local_key))
    user = env.user

    home = silent_sudo('pwd').strip()
    ssh_dir = os.path.join(home, '.ssh')
    with settings(warn_only=True):
        mkdir(ssh_dir)
    chmod(777, ssh_dir)
    with open(local_key) as handle:
        files.append(os.path.join(ssh_dir, 'authorized_keys'), handle.read())
    chmod(700, ssh_dir)
    chown(user, ssh_dir)
    chgrp(group(), ssh_dir)


@bootstrap.register('darwin')
def bootstrap_osx_homebrew(master, minion, upgrade):
    "Bootstraps OSX to be a salt minion or master using homebrew as the base"
    upload_key()

    # TODO: support env.salt_bleeding

    remove('/tmp/homebrew')
    git.using(sudo)('clone https://github.com/mxcl/homebrew.git /tmp/homebrew')
    sudo('rsync -axSH /tmp/homebrew/ /usr/local/')
    chmod('775', '/usr/local/')
    chown('root', '/usr/local/')
    chgrp('staff', '/usr/local/')
    with cd('/usr/local/'):
        sudo('git clean -fd')

    brew_install('swig')
    brew_install('zmq')
    brew_install('python')
    run('pip install salt')

    # increase max files limit (os default is 256...)
    # salt-masters need at least 2x the number of clients
    sudo('launchctl limit maxfiles 10000')
    context = dict(python=run('which python'),
                   salt_master=run('which salt-master'),
                   salt_minion=run('which salt-minion'))

    if master:
        config_template_upload('osx/org.saltstack.salt-master.plist', '/Library/LaunchDaemons/org.saltstack.salt-master.plist',
                               context=None, use_sudo=True)
        sudo('launchctl load -w /Library/LaunchDaemons/org.saltstack.salt-master.plist')
    if minion:
        config_template_upload('osx/org.saltstack.salt-minion.plist', '/Library/LaunchDaemons/org.saltstack.salt-minion.plist',
                               context=None, use_sudo=True)
        sudo('launchctl load -w /Library/LaunchDaemons/org.saltstack.salt-minion.plist')


@bootstrap.register('linux')
def bootstrap_linux(master, minion, upgrade):
    "Uses salt bootstrapping to setup the remote server with salt"
    upload_key()
    if upgrade:
        apt_update()
        apt_upgrade()
        reboot_if_required()

    args = []
    if master:
        args.append('-M')
    if not minion:
        args.append('-N')
    if env.salt_bleeding:
        args.append(repr(env.salt_bleeding))

    context = dict(
        sh="sh -s -- {0}".format(' '.join(args)),
        url=env.salt_bootstrap
    )
    if has('wget'):
        sudo("wget -O - {url!r} | {sh}".format(**context))
    elif has('curl'):
        sudo("curl -L {url!r} | {sh}".format(**context))
    elif has('fetch'):
        sudo('fetch -o - {url!r} | {sh}'.format(**context))
    elif has('python'):
        sudo('python -c \'import urllib; print urllib.urlopen("{url}").read()\' | {sh}'.format(**context))
    else:
        raise TypeError('Unable to download and run bootstrap script! ({url!r} | {sh})'.format(**context))


@roles('minion')
def minion(master, hostname, roles=()):
    """Sets up the salt-minion on the remote server.
    Argument should be the ip address of the salt master.
    """
    upload_minion_key(hostname)
    upload_minion_config(master, roles)


@task
@requires_host
def hostname(name='', fqdn=True):
    "Gets or sets the machine's hostname"
    if name:
        previous_host = run('hostname').strip()
        print "Set hostname {0} => {1}".format(repr(previous_host), repr(name))
        sudo('hostname ' + name)
        sudo('echo {0} > /etc/hostname'.format(name))
        files.sed('/etc/hosts', previous_host, name, use_sudo=True)
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


def config_template_upload(filename, dest, context=None, use_sudo=True):
    context = context or {}
    for config in env.configs:
        filepath = os.path.relpath(os.path.join('configurations', config, filename))
        context['__file__'] = filepath
        if os.path.exists(filepath):
            print 'Use template:', filepath
            files.upload_template(filepath, dest, context=context, use_jinja=True, use_sudo=use_sudo)
            return
        else:
            print '[warn] Template {0} does not exist', repr(filepath)
    raise TypeError('Could not find {0} to upload in any configuration!'.format(repr(filename)))


def salt_config_context(roles=(), **kwargs):
    kwargs.update({
        'saltfiles': SALT_DIR,
        'configs': env.configs,
        'roles': roles,
    })
    return kwargs

@task
@roles('master')
def upload_master_config():
    "Uploads master config to the remote server and restarts the salt-master."
    config_template_upload('master', '/etc/salt/master', context=salt_config_context())
    service('salt-master', 'stop')
    silent_sudo('pkill salt-master') # to ensure it gets killed
    time.sleep(1)
    service('salt-master', 'start')


@task
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
    if sync:
        salt('saltutil.refresh_pillar')
        salt('saltutil.sync_all')

def reboot_if_required():
    """Reboots the machine only if the system indicates a restart is required for updates.
    """
    out = silent('[ -f /var/run/reboot-required ]')
    if not out.return_code:
        print "System requires reboot => Rebooting NOW"
        reboot()
