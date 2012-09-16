import time

from fabric.api import sudo, run, local, settings, hide, env
from fabric.utils import puts as _puts

def puts(*args):
    if not args:
        args = ('',)
    _puts(*args, show_prefix=len(env.hosts) > 1, flush=True)

class Apt(object):
    name = 'apt'
    def update(self):
        return sudo('apt-get update -yq')
        
    def upgrade(self):
        return sudo('apt-get upgrade -yq')
        
    def install(self, *pkgs):
        return sudo('apt-get install -yq ' + ' '.join(pkgs))
        
    def remove(self, *pkgs):
        return sudo('apt-get remove -yq ' + ' '.join(pkgs))
        
    def clean(self):
        return sudo('apt-get autoremove -yq')
            
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

def silent(cmd, use_sudo=False):
    """Performs operations silently (no output). Does not explode when running this command.

    This is useful for checking for existance of things without blowing up on bad exit codes
    (such as using which).
    """
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        if use_sudo:
            return sudo(cmd)
        else:
            return run(cmd)

def has(app, which='which %(app)s', use_sudo=True):
    "Returns true if the given binary exists. Uses which by default."
    return not silent(which % {'app': app}, use_sudo=use_sudo).failed

def is_distro(name):
    "Checks if linux distro matches."
    return not silent('grep %r /etc/issue -i -q' % name).failed

def service(service, action):
    "Manages the execution of services."
    # bleeding edge deployment
    if has('/opt/saltstack', which='test -e %(app)s', use_sudo=True):
        if action == 'stop':
            silent('pkill {0}'.format(service), use_sudo=True)
            time.sleep(1)
        elif action == 'start':
            sudo('{0} -d'.format(service))
        else:
            raise TypeError('Invalid service action: {0}'.format(action))
        return
    # normal deploy
    if is_distro('ubuntu'):
        sudo('service %s %s' % (service, action))
    else:
        sudo('/etc/init.d/%s %s' % (service, action))


def add_host(name, password=None):
    """Helper method to add a host with a password. This is used more for testing.

    YOU REALLY SHOULDN'T ADD PASSWORDS HERE.
    """
    env.hosts += [name]

    if password is None:
        return
    env.passwords[name] = password
