import os
from StringIO import StringIO
from urlparse import urlparse
from urllib2 import urlopen
from functools import wraps

from fabric.api import settings, hide, sudo, env, task, puts
from fabric.contrib.project import rsync_project
import requests


class WithStringIO(StringIO):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self

def sync_dir(local_dir, remote_dir, exclude=()):
    "Syncs a local directory to a remote directory"
    if not local_dir.endswith('/'):
        local_dir += '/'
    puts('rsync {0} => {1}'.format(local_dir, remote_dir))
    with settings(hide('warnings', 'stdout', 'stderr')):
        rsync_project(
            remote_dir=remote_dir,
            local_dir=local_dir,
            exclude=('.git', '*.pyc', '*.pyo') + tuple(exclude),
            delete=True,
        )

def silent(cmd):
    "Returns the given command without printing stdout or stderr."
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        return sudo(cmd)


def silent_sudo(cmd):
    "Shortcut to silent(cmd, use_sudo=True)"
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        return sudo(cmd)

def boolean(value):
    "Coerces a string value into a boolean"
    return str(value).lower() in (
        'yes', 'y', '1', 'true', 't', 'ok', 'on', 'enabled', 'enable'
    )

def group():
    "Returns the root / admin group. Uses root unless OSX, where the group is staff"
    group = env.user
    is_darwin = not silent_sudo('uname | grep -iq darwin').failed
    if is_darwin:
        group = 'staff'
    return group

def check_for_sudo(fn):
    """Wraps a task to with a sudo command to avoid sudo warning messages
    from potentially tampering with sudo commands that expect output.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        silent_sudo('echo test')
        return fn(*args, **kwargs)
    return wrapper

def get_config(servers):
    "Gets the Configuration instance for the current server."
    server_name = env.servers[env.host_string]['name']
    return servers.configuration_for_server(server_name)

def get_operating_system(detectors):
    "Returns the operating system type."
    for cmd in detectors:
        command = cmd.keys()[0]
        detect = cmd.values()[0]
        system = sudo(command).strip().lower()
        for name, opsys in detect.items():
            if name in system:
                return opsys
    raise TypeError('Unknown Operating System: ' + system)

def open_file(url, configuration):
    """Returns an open file handle.

    Unlike open, this is aware of various schemes:
        - file (filepath)
        - http (makes a web request)
        - https (makes a web request)
        - salt (looks up the file in the configurations directory

    If no scheme is provided, it is assumed to be a local file path.
    """
    uri = urlparse(url)
    scheme = uri.scheme.lower().strip()
    if scheme in ('file', ''):
        return open(uri.path)
    if scheme == 'salt':
        return open(configuration.find_file(uri.netloc + uri.path))
    if scheme in ('http', 'https'):
        return WithStringIO(requests.get(url).text)
    raise TypeError('Cannot open url: ' + repr(url))


def generate_server_names_as_tasks(servers, global_vars):
    """Generates tasks for all the servers specified in servers.yml
    """
    def set_server(name, server):
        def fn():
            hostname = server['host']
            env.hosts.append(hostname)
            if 'password' in server:
                env.passwords[hostname] = server['password']
            env.servers[hostname] = server
        fn.__name__ = name
        return fn

    for name, server in servers.items():
        global_vars[name] = task(set_server(name, server))

