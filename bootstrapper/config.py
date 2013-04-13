import json
import os

from fabric.api import task, env, sudo
from fabric.state import output

from bootstrapper.helpers import boolean, download, is_platform

SALT_DIR = '/opt/salt/'
CONFIG_DIR = os.path.abspath('configurations')
env.configs = ['base']
env.salt_bleeding = False
env.salt_roles = []
env.salt_bootstrap = 'https://raw.github.com/jeffh/salt-bootstrap/develop/bootstrap-salt.sh'
env.group = None
env.hostnames = {}

def group():
    if env.group is None:
        env.group = env.user
        if is_platform('darwin'):
            env.group = 'staff'
    return env.group

def master_minions_dir():
    "Returns the directory for the master's minion keys directory"
    ver = tuple(map(int, sudo('salt-master --version | cut -f 2 -d " "').strip().split('.')))
    if ver[0] == 0 and ver[1] < 11: # < 0.11.0
        return '/etc/salt/pki/minions'
    else:
        return '/etc/salt/pki/master/minions'

def minion_key_path():
    "Returns the directory for hhe minion pub/priv key directory."
    ver = tuple(map(int, sudo('salt-minion --version | cut -f 2 -d " "').strip().split('.')))
    if ver[0] == 0 and ver[1] < 11: # < 0.11.0
        return '/etc/salt/pki'
    else:
        return '/etc/salt/pki/minion'


############################# CONFIGURATION #########################    
@task
def include(name):
    """Adds configuration types, separated by spaces. Can optionally be called multiple times.
    Base config is always included by default.

    Ex:
        fab config:yacs config:foo
        fab config:"yacs foo" # same as above
    """
    env.configs = name.split(' ') + env.configs


@task
def roles(*args):
    """Sets the roles assign to the targeted machine. Can provide a comma-separated
    list of roles.
    
    The salt master will always include the 'salt-master' role.
    
    Example:
    
        fab roles:yacs,db deploy_minion
    """
    env.salt_roles.extend(args)


@task
def develop(ref='develop'):
    "Makes salt deployments use bleeding edge or a given ref."
    env.salt_bleeding = ref


def download_package(url, path, expected_hash):
    """
    Downloads the given package into the configuration system (to test out)
    """
    path = package_path(path, configuration)
    print '[{0}]'.format(configuration), 'GET', url
    print '       =>', rel_package_path(path)
    download(url, path, expected_hash)


@task
def remove_external_files():
    "Removes all downloaded packages"
    with open('external_files.json', 'r') as handle:
        data = json.loads(handle.read())
    for name, packages in data.items():
        for package in packages:
            path = os.path.abspath(package['path'])
            if os.path.exists(path):
                print package['path']
                os.unlink(path)


@task
def download_external_files(everything=False):
    "Downloads all the package files for seafood states"
    with open('external_files.json', 'r') as handle:
        data = json.loads(handle.read())
    for name, packages in data.items():
        if not boolean(everything):
            packages = [packages[0]]
        for package in packages:
            print name, '=>', package['path']
            path = os.path.abspath(package['path'])
            download(package['url'], path, package['sha256'])
    print 'Done'

