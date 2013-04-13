import time
import hashlib
import os
import shutil
from functools import wraps
from collections import defaultdict
from contextlib import contextmanager

from fabric.api import sudo, run, local, settings, hide, env, task
from fabric.utils import puts
from fabric.contrib.project import rsync_project

import bootstrapper.config

        
def silent(cmd):
    "Returns the given command without printing stdout or stderr."
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        return sudo(cmd)

def silent_sudo(cmd):
    "Shortcut to silent(cmd, use_sudo=True)"
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        return sudo(cmd)

class Command(object):
    def __init__(self, format='{args} {kwargs}', using=None, then=None):
        self.fmt = str(format)
        self._usingfn = using or sudo
        self._thenfn = then or (lambda x: x)

    def using(self, fn):
        return Command(self.fmt, fn, self._thenfn)

    def then(self, fn):
        return Command(self.fmt, self._usingfn, fn)

    def string(self, *args, **kwargs):
        "Returns the command to execute"
        kwargs_sb = []
        for key, value in kwargs.items():
            kwargs_sb.append('{0}={1!r}'.format(key, value))
        return self.fmt.format(
            args=' '.join(map(repr, args)),
            kwargs=' '.join(kwargs_sb),
        )

    def __call__(self, *args, **kwargs):
        return self._thenfn(self._usingfn(self.string(*args, **kwargs)))

    def __repr__(self):
        return '<Command: {using}({fmt!r}) -> {fn!r}'.format(
            using=self._usingfn,
            fmt=self.fmt,
            fn=self._thenfn,
        )

def __return_succeeded(cmd):
    return not cmd.failed

apt_update = Command('apt-get update -yq {kwargs} {args}')
apt_upgrade = Command('DEBIAN_FRONTEND=noninteractive apt-get upgrade -yq -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" {kwargs} {args}')
apt_install = Command('DEBIAN_FRONTEND=noninteractive apt-get install -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" -yq --force-yes {kwargs} {args}')
apt_remove = Command('apt-get remove -yq {kwargs} {args}; true')
apt_clean = Command('apt-get autoremove -yq {kwargs} {args}')
apt_has = Command('apt-cache show {kwargs} {args}')

has = Command('which {args}').using(silent_sudo).then(__return_succeeded)
is_platform = Command('uname | grep -iq {kwargs} {args}').using(silent_sudo).then(__return_succeeded)
is_distro = Command('grep {args} /etc/issue -i -q {kwargs}').using(silent_sudo).then(__return_succeeded)
remove = Command('rm -rf {kwargs} {args}')
silent_remove = remove.using(silent_sudo)
move = Command('mv -f {kwargs} {args}')
copy = Command('cp -r {kwargs} {args}')
chown = Command('chown -R {kwargs} {args}')
chgrp = Command('chgrp -R {kwargs} {args}')
chmod = Command('chmod -R {kwargs} {args}')
mkdir = Command('mkdir -p {kwargs} {args}')
silent_mkdir = mkdir.using(silent_sudo)

salt = Command("salt '*' {args}")
git = Command("git {args} {kwargs}")
brew_install = Command("brew install {args} {kwargs}")

def identity(x):
    return x

class Dispatcher(object):
    def __init__(self, name, dispatch=identity, doc=None):
        self.fns = {}
        self.name = name
        self.dispatch = dispatch
        self.argmapper = lambda x: x
        self.beforefn = None
        self.afterfn = None
        self.__doc__ = doc

    def register(self, key):
        def decorator(fn):
            self.fns[key] = fn
            return fn
        return decorator

    def map_args_with(self, fn):
        "Takes all incoming args to the dispatcher (not kwargs) and applys fn to it."
        self.argmapper = fn
        return self

    def before(self, fn):
        "Sets the a function to be invoked before a dispatch function is called"
        self.beforefn = fn
        return self

    def after(self, fn):
        "Sets the function to be invokes after a dispatch function is called"
        self.afterfn = fn
        return self

    def __call__(self, *args, **kwargs):
        for key, fn in self.fns.items():
            if self.dispatch(key):
                if self.beforefn:
                    self.beforefn(*args, **kwargs)
                fn(*tuple(map(self.argmapper, args)), **kwargs)
                if self.afterfn:
                    self.afterfn(*args, **kwargs)
                return
        raise TypeError("Failed to dispatch {0!r}".format(self.name))


def service(service, action):
    "Manages the execution of services."
    # bleeding edge deployment)
    if has('/opt/saltstack', which='test -e %(app)s', use_sudo=True):
        if 'stop' in action:
            silent_sudo('pkill {0}'.format(service))
            time.sleep(1)
        elif action == 'start':
            sudo('{0} -d'.format(service))
        else:
            raise TypeError('Invalid service action: {0}'.format(action))
        return
    # normal deploy
    if has('service'):
        sudo('service %s %s' % (service, action))
    else:
        sudo('/etc/init.d/%s %s' % (service, action))

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

def add_host(name, password=None, roles=None, hostname=None):
    """Helper method to add a host with a password. This is used more for testing.
    """
    if roles:
        env.roledefs = env.roledefs or defaultdict(list)
        for role in roles:
            env.roledefs[role].append(name)
    print 'Added host target:', name
    env.hosts += [name]

    if hostname:
        env.hostnames[name] = hostname

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


def sync_dir(local_dir, remote_dir, exclude=()):
    "Syncs a local directory to a remote directory"
    if not local_dir.endswith('/'):
        local_dir += '/'
    rsync_project(
        remote_dir=remote_dir,
        local_dir=local_dir,
        exclude=('.git', '*.pyc', '*.pyo') + tuple(exclude),
        delete=True,
    )

class _HashStreamWrapper(object):
    "A wrapper that produces a hash from a requests stream"
    def __init__(self, stream, hash):
        self.stream, self.hash = stream, hash
        
    def read(self, size):
        content = self.stream.read(size)
        self.hash.update(content)
        return content
    
    def hexdigest(self):
        return self.hash.hexdigest()

def download(url, path, expected_hash):
    "Downloads a given file to its path and verifies its sha256 hash"
    try:
        import requests
    except ImportError:
        raise ImportError("requests library missing. Did you forget to 'pip install -r requirements.txt'?")
    parent = os.path.dirname(path)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    
    if os.path.exists(path):
        hasher = hashlib.sha256()
        with open(path, 'r') as h:
            content = h.read(10)
            while content:
                hasher.update(content)
                content = h.read(10)
        if hasher.hexdigest() == expected_hash:
            return 

    with open(path, 'w+') as h:
        resp = requests.get(url, stream=True)
        wrapper = _HashStreamWrapper(resp.raw, hashlib.sha256())
        shutil.copyfileobj(wrapper, h)
    message = 'Expected md6 hash {0} to be equal to expected hash {1}'.format(
        repr(wrapper.hexdigest()),
        repr(expected_hash),
    )
    assert wrapper.hexdigest() == md5hash, message

