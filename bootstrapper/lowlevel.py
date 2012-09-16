"""All low-level tasks that the highlevel module invokes
"""
import os
import sys
import time

from fabric.api import reboot, task, env, sudo, runs_once, local, settings, cd, run
from fabric.contrib import files
from fabric.contrib.project import upload_project
from fabric import operations


from bootstrapper.config import CONFIG_DIR, SALT_DIR
from bootstrapper.helpers import silent, is_distro, puts, find_pkgmgr, service


@task
def upgrade_all_packages():
    "Updates all packages"
    puts(" - Upgrading existing packages")
    find_pkgmgr().upgrade()
    reboot_if_required()


@task
def convert_to_bleeding():
    "Converts the master installation to bleeding edge."
    pkgmgr = find_pkgmgr()
    pkgmgr.install('salt-common')
    silent('pkill salt-master', use_sudo=True)
    silent('pkill salt-minion', use_sudo=True)
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


@task
def upgrade_bleeding():
    "Upgrades the bleeding edge and reinstall it."
    service('salt-master', 'stop')
    service('salt-minion', 'stop')
    time.sleep(1)
    with cd('/opt/saltstack/'):
        sudo('git pull origin master')
        sudo('python setup.py install')
        service('salt-master', 'start')
        service('salt-minion', 'start')

@task
def bootstrap_with_aptget(upgrade):
    "Bootstraps installation of saltstalk on the remote machine"
    apt = find_pkgmgr()
    puts(" - Found Apt")
    puts(" - Updating repositories")
    apt.update()
    
    requires_update = True
    
    if is_distro('ubuntu'):
        puts(" - System is Ubuntu:")
        puts("   - Installing python-software-properties (to add remote repository)")
        apt.install('python-software-properties')
        puts("   - Adding saltstack repository")
        sudo('add-apt-repository ppa:saltstack/salt -y')
    elif is_distro('debian'):
        puts(" - System is Debian")
        if not apt.has('salt-master'):
            puts("   - Adding debian backports to repositories")
            sudo('''cat <<EOF | sudo tee /etc/apt/sources.list.d/backports.list
deb http://backports.debian.org/debian-backports squeeze-backports main
EOF''')
        else:
            puts("   - Already has salt packages")
            requires_update = False
    else:
        raise TypeError("Unknowned OS")

    if upgrade:
        upgrade_all_packages()
    
    if requires_update:
        puts(" - Updating repositories to fetch salt packages")
        apt.update()


@task
def bootstrap(upgrade=0):
    "Performs a bootstrap depending on the operating system."
    pkgmgr = find_pkgmgr()
    bootstrappers = {
        'apt': bootstrap_with_aptget,
    }
    puts("Bootstrapping system:")
    bootstrappers[pkgmgr.name](int(upgrade))
    puts()


@task
def minion(master, pub_key=None, priv_key=None, develop=False):
    """Sets up the salt-minion on the remote server.
    Argument should be the ip address of the salt master.
    
    NOTE: will remove local public and private keys of the minion if provided!
    """
    puts("Setting up machine as minion:")
    pkgmgr = find_pkgmgr()
    puts(" - Add salt => {0} in /etc/hosts".format(master))
    files.append('/etc/hosts', '{0}\tsalt'.format(master), use_sudo=True)
    if not pub_key and not priv_key:
        if os.path.exists('minion.pub') and os.path.exists('minion.pem'):
            puts(" - Found pub/priv keys locally to use (minion.pub & minion.pem)")
            pub_key, priv_key = map(os.path.abspath, ['minion.pub', 'minion.pem'])
        else:
            puts()
            puts("ERROR: public and private keys are not available...")
            sys.exit(1)
    if os.path.exists(pub_key) and os.path.exists(priv_key):
        puts(" - Uploading Keys:")
        silent('rm -f /etc/salt/pki/minion.pub /etc/salt/pki/minion.pem', use_sudo=True)
        silent('mkdir -p /etc/salt/pki', use_sudo=True)
        silent('chmod -R 644 /etc/salt/', use_sudo=True)
        silent('chown -R root /etc/salt/', use_sudo=True)
        silent('chgrp -R root /etc/salt/', use_sudo=True)
        pub_key, priv_key = map(os.path.abspath, (pub_key, priv_key))
        pub_key_dest, priv_key_dest = '/etc/salt/pki/minion.pub', '/etc/salt/pki/minion.pem'
        puts("   - uploading public key")
        files.put(pub_key, pub_key_dest, use_sudo=True)
        puts("   - uploading private key")
        files.put(priv_key, priv_key_dest, use_sudo=True)
        puts(" - Removing local keys")
        local('rm -f %s %s' % (pub_key, priv_key))
    else:
        puts(" - No keys provided to minion (you'll have to authenticate with master manually)")

    puts(" - Installing salt-minion")
    pkgmgr.install('salt-minion')

    if env.salt_bleeding:
        convert_to_bleeding()
        time.sleep(1)
        service('salt-minion', 'start')

    upload_minion_config()
    puts()


@task
def master():
    "Sets up the salt-master on the remote server."
    puts("Setting up machine as master:")
    puts(" - Installing salt-master")
    find_pkgmgr().install('salt-master')
    if env.salt_bleeding:
        convert_to_bleeding()
        service('salt-master', 'start')
    upload_master_config()
    puts()


@task
def upload_master_config():
    "Uploads master config to the remote server and restarts the salt-master."
    puts("Configuring Master:")
    context = {'saltfiles': SALT_DIR, 'configs': env.configs}
    puts(" - upload /etc/salt/master (context: %r)" % (context,))
    files.upload_template('master', '/etc/salt/master', context=context, use_jinja=True, use_sudo=True)
    puts(" - Rebooting master")
    service('salt-master', 'stop')
    silent('pkill salt-master', use_sudo=True) # to ensure it gets killed
    time.sleep(1)
    service('salt-master', 'start')
    puts()


@task
def upload_minion_config():
    "Uploads the minion config to the remote server and restarts the salt-minion."
    puts("Configuring Minion:")
    context = {'saltfiles': SALT_DIR, 'configs': env.configs}
    puts(" - upload /etc/salt/minion (context: {0})".format(repr(context)))
    files.upload_template('minion', '/etc/salt/minion', context=context, use_jinja=True, use_sudo=True)
    puts(" - Rebooting minion")
    service('salt-minion', 'stop')
    silent('pkill salt-minion', use_sudo=True)
    time.sleep(1)
    service('salt-minion', 'start')
    puts()


@task
def upload():
    "Uploads all pillars, modules, and states to the remote server."
    puts("Uploading Salt Data:")
    puts(" - Clearing existing data")
    sudo('rm -rf {0}'.format(SALT_DIR))
    sudo('mkdir -p {0}'.format(SALT_DIR))
    for system in env.configs:
        puts(" - Upload configuration: " + system)
        for dirname in ('states', 'pillars'):
            src = os.path.join(CONFIG_DIR, system, dirname)
            path = os.path.join(SALT_DIR, system)
            dest = os.path.join(path, dirname)
            puts("    - {0}/{1}".format(system, dirname))
            upload_project(src)
            # remove dot files
            sudo('find {0} -name ".*" | xargs rm -rf'.format(dirname))
            # remove pyc files
            sudo('find {0} -name "*.pyc" | xargs rm -rf'.format(dirname))
            with settings(warn_only=True):
                sudo('mkdir -p {0}'.format(path))
                sudo('mv {0} {1}'.format(dirname, dest))
    puts(" - Syncing pillar data to minions")
    sudo("salt '*' saltutil.refresh_pillar")
    puts(" - Syncing states and modules to minions")
    sudo("salt '*' saltutil.sync_all")
    puts()


@task
def generate_minion_key(hostname, keys_dir='/etc/salt/pki/minions/'):
    """Creates the minion key from the given host and download it locally
    (as minion.pem and minion.pub).
    """
    puts("Generating Minion Key from Master:")
    puts(" - Removing existing keys for minion")
    silent('rm -f {0}{1}.pub {0}{1}.pem'.format(keys_dir, hostname, hostname), use_sudo=True)
    puts(" - Generating keys for {0}".format(repr(hostname)))
    sudo('salt-key --gen-keys={0}'.format(hostname))
    puts(" - Adding public key to master's keylist")
    sudo('cp {0}.pub {1}{2}'.format(hostname, keys_dir, hostname))
    sudo('chmod +r {0}.pem {1}.pub'.format(hostname, hostname))
    puts(" - GET minion.pem")
    operations.get('{0}.pem'.format(hostname), 'minion.pem')
    puts(" - GET minion.pub")
    operations.get('{0}.pub'.format(hostname), 'minion.pub')
    sudo('rm -f {0}.pem {1}.pub'.format(hostname, hostname))
    puts()
    return [os.path.abspath(x) for x in ('minion.pem', 'minion.pub')]


@task
def hostname(name='', fqdn=True):
    "Gets or sets the machine's hostname"
    if name:
        previous_host = run('hostname').strip()
        puts("Setting hostname {0} => {1}".format(repr(previous_host), repr(name)))
        sudo('hostname ' + name)
        sudo('echo {0} > /etc/hostname'.format(name))
        files.sed('/etc/hosts', previous_host, name, use_sudo=True)
    else:
        return sudo('hostname {0}'.format('-f' if fqdn else ''))


@task
def reboot_if_required():
    """Reboots the machine only if the system indicates a restart is required for updates.
    """
    out = silent('[ -f /var/run/reboot-required ]')
    if not out.return_code:
        puts("System requires reboot => Rebooting NOW")
        reboot()
