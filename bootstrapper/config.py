import sys
import os
from StringIO import StringIO

from fabric.api import task, env, sudo
from fabric.state import output

from bootstrapper.helpers import runner

# set fabric's default verbosity to be a minimal.
output['everything'] = False
output['user'] = True

SALT_DIR = '/opt/salt/'
CONFIG_DIR = os.path.abspath('configurations')
env.configs = ['base']
env.salt_bleeding = False
env.salt_roles = []

runner.types['state'] = sys.stdout
runner.types['action'] = sys.stdout

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
def verbose():
    """Re-enables fabric's verbosity."""
    output['everything'] = True
    runner.types['state'] = runner.types['action'] = StringIO()
    runner.types['ALL'] = sys.stdout


@task
def quiet():
    "Suppresses most output."
    output['everything'] = False
    output['user'] = True
    runner.types['cmd'] = runner.types['state'] = runner.types['ALL'] = StringIO()
    runner.types['action'] = sys.stdout

@task
def develop(repo='git://github.com/saltstack/salt.git'):
    "Makes salt deployments use git repository."
    env.salt_bleeding = repo
