import time
import sys
from functools import wraps
from collections import defaultdict
from StringIO import StringIO
from contextlib import contextmanager

from fabric.api import sudo, run, local, settings, hide, env, task
from fabric.utils import puts

class Fabric:
    def __init__(self):
        self.prefixes = []
        self.types = defaultdict(StringIO)
        
    def log(self, level, message, *args, **kwargs):
        logger = self.types[level]
        string = ''.join(self.prefixes) + message.format(*args, **kwargs) + '\n'
        logger.write(string)
        logger.flush()
        self.types['ALL'].write(string)
        self.types['ALL'].flush()
        return self
        
    @contextmanager
    def with_prefix(self, prefix):
        self.add_prefix(prefix)
        yield
        self.pop_prefix()
        
    @contextmanager
    def try_then_log(self, prefix, type, *message, **kwargs):
        try:
            yield
        except:
            self.add_prefix('[{0}:error] '.format(prefix))
            self.log(type, *message, **kwargs)
            self.pop_prefix()
            raise
        else:
            self.add_prefix('[{0}] '.format(prefix))
            self.log(type, *message, **kwargs)
            self.pop_prefix()
        
    def run(self, cmd, *args, **kwargs):
        "Runs a given command and logs it"
        with self.try_then_log('run', 'cmd', cmd):
            return run(cmd, *args, **kwargs)
        
    def sudo(self, cmd, *args, **kwargs):
        "Runs a given command as sudo and logs it"
        with self.try_then_log('sudo', 'cmd', cmd):
            return sudo(cmd, *args, **kwargs)
            
    def silent(self, cmd, use_sudo=False):
        "Returns the given command without printing stdout or stderr."
        with self.try_then_log(('slient-sudo' if use_sudo else 'silent-run'), 'cmd', cmd):
            with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
                if use_sudo:
                    return sudo(cmd)
                else:
                    return run(cmd)
        
    def state(self, *message, **kwargs):
        self.log('state', *message, **kwargs)
        return self
        
    def action(self, *message, **kwargs):
        self.log('action', *message, **kwargs)
        return self
        
    def warn(self, *message, **kwargs):
        self.log('warn', *message, **kwargs)
        return self
    
    def add_prefix(self, prefix):
        self.prefixes.append(prefix)
        return self
        
    def pop_prefix(self):
        self.prefixes.pop()
        return self
        
runner = Fabric()

class Apt(object):
    name = 'apt'
    def update(self):
        runner.state('Update sources')
        return runner.sudo('apt-get update -yq')
        
    def upgrade(self):
        runner.state('Upgrade packages')
        return runner.sudo('DEBIAN_FRONTEND=noninteractive apt-get upgrade -yq -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"')
        
    def install(self, *pkgs):
        runner.state('Install: {0}', ', '.join(pkgs))
        return runner.sudo('DEBIAN_FRONTEND=noninteractive apt-get install -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" -yq --force-yes ' + ' '.join(pkgs))
        
    def remove(self, *pkgs):
        runner.state('Uninstall: {0}', ', '.join(pkgs))
        return runner.sudo('apt-get remove -yq {0}; true'.format(' '.join(pkgs)))
        
    def clean(self):
        runner.state('Cleaning up...')
        return runner.sudo('apt-get autoremove -yq')
            
    def has(self, *pkgs):
        for pkg in pkgs:
            if not has(pkg, 'apt-cache show %(app)s'):
                return False
        return True
        
def find_pkgmgr():
    "Returns the OS-specific package manager"
    if has('apt-get'):
        return Apt()
    raise TypeError("Could not determine operating system's package manager!")

def has(app, which='which %(app)s', use_sudo=True):
    "Returns true if the given binary exists. Uses which by default."
    return not runner.silent(which % {'app': app}, use_sudo=use_sudo).failed

def is_distro(name):
    "Checks if linux distro matches."
    return not runner.silent('grep %r /etc/issue -i -q' % name).failed

def service(service, action):
    "Manages the execution of services."
    # bleeding edge deployment)
    if has('/opt/saltstack', which='test -e %(app)s', use_sudo=True):
        if 'stop' in action:
            runner.silent('pkill {0}'.format(service), use_sudo=True)
            time.sleep(1)
        elif action == 'start':
            runner.sudo('{0} -d'.format(service))
        else:
            raise TypeError('Invalid service action: {0}'.format(action))
        return
    # normal deploy
    if has('service'):
        runner.sudo('service %s %s' % (service, action))
    else:
        runner.sudo('/etc/init.d/%s %s' % (service, action))

def requires_host(fn):
    """A decorator that checks if env.hosts is set before proceeding."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        assert env.hosts or env.roledefs, "No host to use. Did you forget to set this?"
        return fn(*args, **kwargs)
    return wrapper


def requires_configuration(fn):
    """A decorator that checks if a env.config is set to more
    than just the base configuration.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        assert list(env.configs) != ['base'], 'No configuration specified. Did you forget to set this?'
        return fn(*args, **kwargs)
    return wrapper


def add_host(name, password=None, roles=None):
    """Helper method to add a host with a password. This is used more for testing.

    YOU REALLY SHOULDN'T ADD PASSWORDS HERE.
    """
    if roles:
        env.roledefs = env.roledefs or defaultdict(list)
        for role in roles:
            env.roledefs[role].append(name)
    runner.state('Added host target: {0}', name)
    env.hosts += [name]

    if password is None:
        return
    env.passwords[name] = password

def boolean(string):
    "Coerces a string value into a boolean, taking in to consideration standard yes value for strings."
    return str(string).strip().lower() in ['true', 'yes', 'y', 't', 'yep', 'yeah', 'ok', '1']

@task
def clear():
    "Removes all added hosts"
    env.hosts = []
    env.roledefs = None
    env.passwords = {}