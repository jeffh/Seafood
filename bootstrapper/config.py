import json
import shutil
import sys
import os
import urllib2
import hashlib
from StringIO import StringIO

from fabric.api import task, env, sudo
from fabric.state import output

from bootstrapper.helpers import runner, boolean

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


class HashStreamWrapper(object):
    def __init__(self, stream, hash):
        self.stream, self.hash = stream, hash
        
    def read(self, size):
        content = self.stream.read(size)
        self.hash.update(content)
        return content
    
    def hexdigest(self):
        return self.hash.hexdigest()


def download_package(url, path, md5hash, configuration='base'):
    """
    Downloads the given package into the configuration system (to test out)
    """
    try:
        import requests
    except ImportError:
        raise ImportError("requests library missing. Did you forget to 'pip install -r requirements.txt'?")
    path = os.path.abspath(os.path.join('configurations', configuration, 'states', 'packages', path))
    parent = os.path.basename(path)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    
    if os.path.exists(path):
        hasher = hashlib.md5()
        with open(path, 'r') as h:
            content = h.read(10)
            while content:
                hasher.update(content)
                content = h.read(10)
        if hasher.hexdigest() == md5hash:
            print '[{0}]'.format(configuration), ' OK', url
            return 

    with open(path, 'w+') as h:
        resp = requests.get(url, stream=True)
        wrapper = HashStreamWrapper(resp.raw, hashlib.md5())
        shutil.copyfileobj(wrapper, h)
    message = 'Expected md6 hash {0} to be equal to expected hash {1}'.format(
        repr(wrapper.hexdigest()),
        repr(md5hash),
    )
    print '[{0}]'.format(configuration), 'GET', url
    assert wrapper.hexdigest() == md5hash, message

@task
def download_package_files(latest_only=True):
    "Downloads all the package files for seafood states"
    with open('packages.json', 'r') as handle:
        data = json.loads(handle.read())
    for conf_name, config in data.items():
        for name, packages in config.items():
            if boolean(latest_only):
                packages = [packages[0]]
            for package in packages:
                download_package(
                    url=package['url'],
                    path=package['path'],
                    md5hash=package['md5'],
                    configuration=conf_name,
                )
    print 'Done'