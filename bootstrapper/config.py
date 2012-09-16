import os

from fabric.api import task, env
from fabric.state import output

# set fabric's default verbosity to be a minimal.
output['everything'] = False
output['user'] = True

SALT_DIR = '/opt/salt/'
CONFIG_DIR = os.path.abspath('configurations')
env.configs = ['base']

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
def verbose():
    """Re-enables fabric's verbosity."""
    output['everything'] = True


@task
def quiet():
    "Suppresses most output."
    output['everything'] = False
    output['user'] = True


@task
def develop(repo='git://github.com/saltstack/salt.git'):
    "Makes salt deployments use git repository."
    env.salt_bleeding = repo
