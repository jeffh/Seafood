"""All low-level tasks that the highlevel module invokes
"""
import os
import sys
import time

from fabric.api import (reboot, env, sudo, runs_once, local,
    settings, cd, run, roles, get, put, parallel, task)
from fabric.contrib import files
from fabric.contrib.project import upload_project
from fabric import operations

from bootstrapper.helpers import (runner, requires_configuration, requires_host,
    silent, is_distro, puts, find_pkgmgr, service)
from bootstrapper.config import CONFIG_DIR, SALT_DIR, MASTER_MINIONS_DIR, MINION_KEY_PATH




def upgrade_all_packages():
    "Updates all packages"
    find_pkgmgr().upgrade()
    reboot_if_required()



def convert_to_bleeding():
    "Converts the master installation to bleeding edge."
    runner.action('Convert Salt to bleeding edge')
    with runner.with_prefix(' ~> '):
        pkgmgr = find_pkgmgr()
        pkgmgr.install('salt-common')
        runner.silent('pkill salt-master', use_sudo=True)
        runner.silent('pkill salt-minion', use_sudo=True)
        time.sleep(1)
        pkgmgr.remove('salt-master')
        pkgmgr.remove('salt-minion')
        pkgmgr.install('git-core')
        silent('rm -rf /opt/saltstack', use_sudo=True)
        silent('mkdir /opt', use_sudo=True)
        with cd('/opt'):
            sudo('git clone {0} {1}'.format(env.salt_bleeding, 'saltstack'))
        with cd('/opt/saltstack/'):
            sudo('python setup.py install')



def upgrade_bleeding():
    "Upgrades the bleeding edge and reinstall it."
    runner.action('Upgrade bleeding edge salt installation')
    with runner.with_prefix(' ~> '):
        service('salt-master', 'stop')
        service('salt-minion', 'stop')
        time.sleep(1)
        with cd('/opt/saltstack/'):
            sudo('git pull origin master')
            sudo('python setup.py install')
            service('salt-master', 'start')
            service('salt-minion', 'start')


def bootstrap_with_aptget(upgrade):
    "Bootstraps installation of saltstalk on the remote machine"
    apt = find_pkgmgr()
    apt.update()

    requires_update = True
    runner.state('Add salt repository')

    if is_distro('ubuntu'):
        apt.install('python-software-properties')
        sudo('add-apt-repository ppa:saltstack/salt -y')
    elif is_distro('debian'):
        if not apt.has('salt-master'):
            runner.state("Add debian backports to repositories")
            sudo('''cat <<EOF | sudo tee /etc/apt/sources.list.d/backports.list
deb http://backports.debian.org/debian-backports squeeze-backports main
EOF''') 
        else:
            runner.state("Already has salt packages")
            requires_update = False
    else:
        raise TypeError("Unknowned OS")

    if upgrade:
        upgrade_all_packages()

    if requires_update:
        apt.update()



def bootstrap(upgrade=1):
    "Performs a bootstrap depending on the operating system."
    runner.action('Bootstrapping salt')
    with runner.with_prefix(' ~> '):
        pkgmgr = find_pkgmgr()
        bootstrappers = {
            'apt': bootstrap_with_aptget,
        }
        silent('rm -rf /etc/salt/')
        silent('rm -rf /opt/salt/')
        bootstrappers[pkgmgr.name](int(upgrade))



@roles('minion')
def minion(master, hostname, roles=(), develop=False):
    """Sets up the salt-minion on the remote server.
    Argument should be the ip address of the salt master.
    """
    runner.action('Set up minion daemon')
    with runner.with_prefix(' ~> '):
        pkgmgr = find_pkgmgr()
        runner.state("Add salt => {0} in /etc/hosts".format(master))
        files.append('/etc/hosts', '{0}\tsalt'.format(master), use_sudo=True)

        runner.state("Install salt-minion")
        pkgmgr.install('salt-minion')

        if env.salt_bleeding:
            convert_to_bleeding()
            time.sleep(1)
            service('salt-minion', 'start')

        upload_minion_key(hostname)
        upload_minion_config(roles)


@task
@parallel
@requires_host
def hostname(name='', fqdn=True):
    "Gets or sets the machine's hostname"
    if name:
        previous_host = run('hostname').strip()
        runner.state("Set hostname {0} => {1}".format(repr(previous_host), repr(name)))
        sudo('hostname ' + name)
        sudo('echo {0} > /etc/hostname'.format(name))
        files.sed('/etc/hosts', previous_host, name, use_sudo=True)
    else:
        return sudo('hostname {0}'.format('-f' if fqdn else '')).strip()



@roles('minion')
def upload_minion_key(hostname, minion_key_dir=None):
    "Installs the minion key generated from the master."
    minion_key_dir = minion_key_dir or MINION_KEY_PATH
    context = dict(hostname=hostname, key_dir=minion_key_dir)
    run('rm -f {hostname} {hostname}.pub'.format(**context))
    put(os.path.join('keys', hostname))
    put(os.path.join('keys', hostname + '.pub'))
    sudo('rm -f {key_dir}/minion.pem; true'.format(**context))
    sudo('rm -f {key_dir}/minion.pub; true'.format(**context))
    sudo('mv {hostname} {key_dir}/minion.pem'.format(**context))
    sudo('mv {hostname}.pub {key_dir}/minion.pub'.format(**context))
    sudo('chown root {key_dir}/minion.pem'.format(**context))
    sudo('chgrp root {key_dir}/minion.pub'.format(**context))
    sudo('chmod 400 {key_dir}/minion.pem'.format(**context))
    sudo('chmod 644 {key_dir}/minion.pub'.format(**context))



@roles('master')
def create_minion_key(hostname, key_dir=None):
    """Geneates a minion key for the given hostname. It then downloads
    the minion keys to the local keys directory for use by
    grab_minion_key.
    
    Must be run on the master host.
    """
    key_dir = key_dir or MASTER_MINIONS_DIR
    context = dict(hostname=hostname, key_dir=key_dir, user=env.user)
    sudo('salt-key --gen-keys={hostname} --gen-keys-dir={key_dir}'.format(**context))
    sudo('mv {key_dir}/{hostname}.pub {key_dir}/{hostname}'.format(**context))
    sudo('cp {key_dir}/{hostname} {hostname}.pub'.format(**context))
    sudo('mv {key_dir}/{hostname}.pem {hostname}'.format(**context))
    sudo('chown {user} {hostname}'.format(**context))
    sudo('chown {user} {hostname}.pub'.format(**context))
    get(hostname, os.path.join('keys', hostname))
    get(hostname + '.pub', os.path.join('keys', hostname + '.pub'))



@roles('master')
def master():
    "Sets up the salt-master on the remote server."
    runner.action('Set up master daemon')
    with runner.with_prefix(' ~> '):
        find_pkgmgr().install('salt-master')
        if env.salt_bleeding:
            convert_to_bleeding()
            service('salt-master', 'start')
        upload_master_config()


def config_template_upload(filename, dest, context={}, use_sudo=True):
    for config in env.configs:
        filepath = os.path.relpath(os.path.join('configurations', config, filename))
        context['__file__'] = filepath
        if os.path.exists(filepath):
            runner.state('Use template: {0}', filepath)
            files.upload_template(filepath, dest, context=context, use_jinja=True, use_sudo=use_sudo)
            return
        else:
            runner.state('Template {0} does not exist', repr(filepath))
    raise TypeError('Could not find {0} to upload in any configuration!'.format(repr(filename)))


def salt_config_context(roles=()):
    return {
        'saltfiles': SALT_DIR,
        'configs': env.configs,
        'roles': roles,
    }


@roles('master')
def upload_master_config():
    "Uploads master config to the remote server and restarts the salt-master."
    runner.state('Upload master configuration')
    config_template_upload('master', '/etc/salt/master', context=salt_config_context())
    runner.state("Reboot master")
    service('salt-master', 'stop')
    silent('pkill salt-master', use_sudo=True) # to ensure it gets killed
    time.sleep(1)
    service('salt-master', 'start')



@roles('minion')
def upload_minion_config(roles=()):
    "Uploads the minion config to the remote server and restarts the salt-minion."
    runner.state('Upload minion configuration')
    config_template_upload('minion', '/etc/salt/minion', context=salt_config_context(roles))
    runner.state("Reboot minion")
    service('salt-minion', 'stop; true')
    silent('pkill salt-minion', use_sudo=True)
    time.sleep(1)
    service('salt-minion', 'start')



@requires_configuration
def upload(sync=True):
    "Uploads all pillars, modules, and states to the remote server."
    runner.action("Upload Salt Data")
    with runner.with_prefix(' ~> '):
        runner.state("Clear existing data")
        sudo('rm -rf {0}'.format(SALT_DIR))
        sudo('mkdir -p {0}'.format(SALT_DIR))
        for system in env.configs:
            runner.state("Upload configuration: " + system)
            for dirname in ('states', 'pillars'):
                src = os.path.join(CONFIG_DIR, system, dirname)
                path = os.path.join(SALT_DIR, system)
                dest = os.path.join(path, dirname)
                runner.state("    - {0}/{1}".format(system, dirname))
                upload_project(src)
                # remove dot files
                sudo('find {0} -name ".*" | xargs rm -rf'.format(dirname))
                # remove pyc files
                sudo('find {0} -name "*.pyc" | xargs rm -rf'.format(dirname))
                with settings(warn_only=True):
                    sudo('mkdir -p {0}'.format(path))
                    sudo('mv {0} {1}'.format(dirname, dest))
        if sync:
            runner.state("Sync pillar data to minions")
            sudo("salt '*' saltutil.refresh_pillar")
            runner.state("Sync states and modules to minions")
            sudo("salt '*' saltutil.sync_all")



def reboot_if_required():
    """Reboots the machine only if the system indicates a restart is required for updates.
    """
    out = silent('[ -f /var/run/reboot-required ]')
    if not out.return_code:
        runner.state("System requires reboot => Rebooting NOW")
        reboot()
